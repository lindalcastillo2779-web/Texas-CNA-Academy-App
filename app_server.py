"""ASGI entrypoint for portal APIs, static assets, and Streamlit proxying."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import os
import subprocess
import sys
from contextlib import asynccontextmanager
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import websockets
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, RedirectResponse, Response
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket, WebSocketDisconnect

from db import (
    apply_stripe_entitlement_update,
    authenticate_user,
    build_admin_portal_payload,
    build_staff_portal_payload,
    build_student_portal_payload,
    create_or_claim_user_account,
    create_portal_session,
    delete_portal_session,
    get_billing_entitlement,
    get_portal_dashboard_path,
    get_portal_profile,
    get_user_by_session_token,
    init_db,
    is_active_license_status,
    is_admin_role,
    is_staff_role,
    normalize_email,
    normalize_role,
    upsert_course_progress,
)

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
COMPILED_DIR = DIST_DIR / "compiled"
ASSET_DIR = BASE_DIR / "assets"
CSS_DIR = BASE_DIR / "css"
PORTAL_DATA_DIR = BASE_DIR / "public" / "portal-data"

COOKIE_NAME = "texas_cna_session"
STREAMLIT_HOST = "127.0.0.1"
STREAMLIT_PORT = int(os.environ.get("STREAMLIT_INTERNAL_PORT", "8501"))
STREAMLIT_BASE_PATH = os.environ.get("STREAMLIT_BASE_PATH", "app").strip("/") or "app"
STREAMLIT_HTTP_BASE = f"http://{STREAMLIT_HOST}:{STREAMLIT_PORT}"
STREAMLIT_WS_BASE = f"ws://{STREAMLIT_HOST}:{STREAMLIT_PORT}"
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()
STRIPE_WEBHOOK_TOLERANCE_SECONDS = int(
    os.environ.get("STRIPE_WEBHOOK_TOLERANCE_SECONDS", "300")
)
STRIPE_CORE_PRICE_IDS = {
    price_id.strip()
    for price_id in os.environ.get("STRIPE_CORE_PRICE_IDS", "").split(",")
    if price_id.strip()
}
STRIPE_PRO_PRICE_IDS = {
    price_id.strip()
    for price_id in os.environ.get("STRIPE_PRO_PRICE_IDS", "").split(",")
    if price_id.strip()
}
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "").strip()
STRIPE_SUCCESS_URL = os.environ.get(
    "STRIPE_SUCCESS_URL", "/dashboard.html?checkout=success"
).strip()
STRIPE_CANCEL_URL = os.environ.get(
    "STRIPE_CANCEL_URL", "/dashboard.html?checkout=cancelled"
).strip()
init_db()


def _dashboard_target(role: str | None) -> str:
    return get_portal_dashboard_path(role)


def _role_requires_facility(role: str) -> bool:
    return role in {"staff", "admin"}


def _session_cookie_secure(request: Request) -> bool:
    return request.url.scheme == "https"


def _set_session_cookie(response: Response, session_token: str, request: Request) -> None:
    response.set_cookie(
        COOKIE_NAME,
        session_token,
        httponly=True,
        samesite="lax",
        secure=_session_cookie_secure(request),
        max_age=60 * 60 * 24 * 7,
        path="/",
    )


def _clear_session_cookie(response: Response, request: Request) -> None:
    response.delete_cookie(
        COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=_session_cookie_secure(request),
        path="/",
    )


def _current_user(request: Request):
    session_token = request.cookies.get(COOKIE_NAME)
    if not session_token:
        return None
    return get_user_by_session_token(session_token)


def _require_user(request: Request):
    user = _current_user(request)
    if user is None:
        raise PermissionError("Please sign in to continue.")
    return user


def _portal_session_payload(user: Any) -> dict[str, Any]:
    profile = get_portal_profile(user)
    return {
        "authenticated": True,
        "user": {
            "id": int(user["id"]),
            "name": user["name"],
            **profile,
            "dashboardPath": _dashboard_target(user["role"]),
        },
    }


def _json_error(message: str, status_code: int) -> JSONResponse:
    return JSONResponse({"error": message}, status_code=status_code)


def _stripe_sql_timestamp(unix_seconds: int | None) -> str | None:
    if not unix_seconds:
        return None
    return datetime.fromtimestamp(int(unix_seconds), tz=timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def _tier_from_price_id(price_id: str | None) -> str | None:
    if not price_id:
        return None
    if price_id in STRIPE_PRO_PRICE_IDS:
        return "pro"
    if price_id in STRIPE_CORE_PRICE_IDS:
        return "core"
    return None


def _determine_tier(metadata: dict[str, Any], price_id: str | None) -> str | None:
    metadata_tier = str(metadata.get("subscription_tier", "")).strip().lower()
    return metadata_tier or _tier_from_price_id(price_id)


def _checkout_is_active(payment_status: str, checkout_status: str) -> bool:
    # Stripe checkout session is treated as active once payment is settled
    # (`payment_status=paid`) or the session status is complete.
    return payment_status == "paid" or checkout_status == "complete"


def _stripe_price_ids(payload: dict[str, Any]) -> list[str]:
    items = payload.get("items")
    data: list[Any] = []
    if isinstance(items, dict):
        data_value = items.get("data")
        if isinstance(data_value, list):
            data = data_value
    price_ids: list[str] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        price = item.get("price")
        if isinstance(price, dict):
            price_id = str(price.get("id", "")).strip()
            if price_id:
                price_ids.append(price_id)
    if not price_ids:
        direct_price = payload.get("price")
        if isinstance(direct_price, dict):
            price_id = str(direct_price.get("id", "")).strip()
            if price_id:
                price_ids.append(price_id)
    return price_ids


def _verify_stripe_signature(payload: bytes, signature_header: str) -> bool:
    parts = [part.strip() for part in signature_header.split(",") if part.strip()]
    signed_timestamp = ""
    signatures: list[str] = []
    for part in parts:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        if key == "t":
            signed_timestamp = value
        elif key == "v1":
            signatures.append(value)
    if not signed_timestamp or not signatures:
        return False

    try:
        timestamp_int = int(signed_timestamp)
    except ValueError:
        return False

    now_utc = int(datetime.now(timezone.utc).timestamp())
    if timestamp_int > now_utc:
        return False
    if now_utc - timestamp_int > STRIPE_WEBHOOK_TOLERANCE_SECONDS:
        return False

    signed_payload = f"{signed_timestamp}.".encode("utf-8") + payload
    expected = hmac.new(
        STRIPE_WEBHOOK_SECRET.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()
    return any(hmac.compare_digest(expected, signature) for signature in signatures)


def _handle_stripe_checkout_completed(payload: dict[str, Any]) -> dict[str, object]:
    metadata = payload.get("metadata") or {}
    customer_details = payload.get("customer_details") or {}
    email = (
        str(customer_details.get("email", "")).strip()
        or str(payload.get("customer_email", "")).strip()
        or str(metadata.get("email", "")).strip()
    )
    price_ids = _stripe_price_ids(payload)
    price_id = price_ids[0] if price_ids else None
    tier = _determine_tier(metadata, price_id)
    payment_status = str(payload.get("payment_status", "")).strip().lower()
    status = str(payload.get("status", "")).strip().lower()
    is_active = _checkout_is_active(payment_status, status)

    return apply_stripe_entitlement_update(
        email=email or None,
        stripe_customer_id=str(payload.get("customer", "")).strip() or None,
        stripe_subscription_id=str(payload.get("subscription", "")).strip() or None,
        stripe_price_id=price_id,
        subscription_active=is_active,
        subscription_tier=tier or None,
        license_status="active" if is_active else "incomplete",
    )


def _handle_stripe_subscription_event(payload: dict[str, Any]) -> dict[str, object]:
    metadata = payload.get("metadata") or {}
    status = str(payload.get("status", "")).strip().lower()
    is_active = is_active_license_status(status)
    price_ids = _stripe_price_ids(payload)
    price_id = price_ids[0] if price_ids else None
    tier = _determine_tier(metadata, price_id)
    subscription_end = _stripe_sql_timestamp(payload.get("current_period_end"))

    return apply_stripe_entitlement_update(
        email=str(metadata.get("email", "")).strip() or None,
        stripe_customer_id=str(payload.get("customer", "")).strip() or None,
        stripe_subscription_id=str(payload.get("id", "")).strip() or None,
        stripe_price_id=price_id,
        subscription_active=is_active,
        subscription_tier=tier or None,
        subscription_expires_at=subscription_end,
        license_status=status or "active",
    )


def _handle_stripe_invoice_event(payload: dict[str, Any], paid: bool) -> dict[str, object]:
    subscription_id = str(payload.get("subscription", "")).strip() or None
    customer_id = str(payload.get("customer", "")).strip() or None
    customer_email = str(payload.get("customer_email", "")).strip() or None
    period_end = _stripe_sql_timestamp(payload.get("period_end"))
    return apply_stripe_entitlement_update(
        email=customer_email,
        stripe_customer_id=customer_id,
        stripe_subscription_id=subscription_id,
        subscription_active=paid,
        subscription_expires_at=period_end,
        license_status="active" if paid else "past_due",
    )


def _handle_stripe_subscription_deleted(payload: dict[str, Any]) -> dict[str, object]:
    metadata = payload.get("metadata") or {}
    price_ids = _stripe_price_ids(payload)
    price_id = price_ids[0] if price_ids else None
    return apply_stripe_entitlement_update(
        email=str(metadata.get("email", "")).strip() or None,
        stripe_customer_id=str(payload.get("customer", "")).strip() or None,
        stripe_subscription_id=str(payload.get("id", "")).strip() or None,
        stripe_price_id=price_id,
        subscription_active=False,
        subscription_tier=_determine_tier(metadata, price_id),
        subscription_expires_at=_stripe_sql_timestamp(
            payload.get("canceled_at") or payload.get("ended_at")
        ),
        license_status="canceled",
    )


async def _read_json(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return payload if isinstance(payload, dict) else {}


async def health(_: Request) -> JSONResponse:
    return JSONResponse({"ok": True})


async def get_session(request: Request) -> JSONResponse:
    user = _current_user(request)
    if user is None:
        return JSONResponse({"authenticated": False, "user": None}, status_code=401)
    return JSONResponse(_portal_session_payload(user))


async def register(request: Request) -> JSONResponse:
    payload = await _read_json(request)
    first_name = str(payload.get("firstName", "")).strip()
    last_name = str(payload.get("lastName", "")).strip()
    email = normalize_email(str(payload.get("email", "")))
    phone = str(payload.get("phone", "")).strip()
    facility = str(payload.get("facility", "")).strip()
    role = normalize_role(str(payload.get("role", "student")))
    password = str(payload.get("password", ""))
    confirm_password = str(payload.get("confirmPassword", ""))

    full_name = " ".join(part for part in [first_name, last_name] if part).strip()
    if not full_name or not email or not password:
        return _json_error("Name, email, and password are required.", 400)
    if len(password) < 8:
        return _json_error("Please choose a password with at least 8 characters.", 400)
    if password != confirm_password:
        return _json_error("Passwords do not match.", 400)
    if _role_requires_facility(role) and not facility:
        return _json_error("Facility or organization name is required for this role.", 400)

    auth_fields = {"password": password}

    try:
        user = create_or_claim_user_account(
            name=full_name,
            email=email,
            role=role,
            phone=phone,
            facility=facility,
            **auth_fields,
        )
    except ValueError as exc:
        return _json_error(str(exc), 409)

    session_token = create_portal_session(int(user["id"]))
    response = JSONResponse(_portal_session_payload(user), status_code=201)
    _set_session_cookie(response, session_token, request)
    return response


async def login(request: Request) -> JSONResponse:
    payload = await _read_json(request)
    email = normalize_email(str(payload.get("email", "")))
    password = str(payload.get("password", ""))
    if not email or not password:
        return _json_error("Email and password are required.", 400)

    user = authenticate_user(email, password)
    if user is None:
        return _json_error("Incorrect email or password.", 401)

    session_token = create_portal_session(int(user["id"]))
    response = JSONResponse(_portal_session_payload(user))
    _set_session_cookie(response, session_token, request)
    return response


async def logout(request: Request) -> JSONResponse:
    session_token = request.cookies.get(COOKIE_NAME)
    if session_token:
        delete_portal_session(session_token)
    response = JSONResponse({"ok": True})
    _clear_session_cookie(response, request)
    return response


async def student_portal(request: Request) -> JSONResponse:
    try:
        user = _require_user(request)
    except PermissionError as exc:
        return _json_error(str(exc), 401)
    if is_staff_role(user["role"]):
        return _json_error("This account does not have student portal access.", 403)

    payload = build_student_portal_payload(int(user["id"]))
    if payload is None:
        return _json_error("Unable to load portal data for this account.", 404)
    return JSONResponse(payload)


async def sync_course_progress(request: Request) -> JSONResponse:
    try:
        user = _require_user(request)
    except PermissionError as exc:
        return _json_error(str(exc), 401)
    if is_staff_role(user["role"]):
        return _json_error("This account does not have student portal access.", 403)

    payload = await _read_json(request)
    module_id = str(payload.get("moduleId", "")).strip().upper()
    completed_lessons_raw = payload.get("completedLessons")

    if not module_id:
        return _json_error("moduleId is required.", 400)
    try:
        completed_lessons = int(completed_lessons_raw)
    except (TypeError, ValueError):
        return _json_error("completedLessons must be an integer.", 400)

    try:
        course_progress = upsert_course_progress(int(user["id"]), module_id, completed_lessons)
    except ValueError as exc:
        return _json_error(str(exc), 400)

    return JSONResponse({"ok": True, "courseProgress": course_progress})


async def staff_portal(request: Request) -> JSONResponse:
    try:
        user = _require_user(request)
    except PermissionError as exc:
        return _json_error(str(exc), 401)
    if not is_staff_role(user["role"]):
        return _json_error("This account does not have staff portal access.", 403)
    return JSONResponse(build_staff_portal_payload())


async def admin_portal(request: Request) -> JSONResponse:
    try:
        user = _require_user(request)
    except PermissionError as exc:
        return _json_error(str(exc), 401)
    if not is_admin_role(user["role"]):
        return _json_error("This account does not have admin portal access.", 403)
    return JSONResponse(build_admin_portal_payload())


async def current_entitlement(request: Request) -> JSONResponse:
    try:
        user = _require_user(request)
    except PermissionError as exc:
        return _json_error(str(exc), 401)

    entitlement = get_billing_entitlement(int(user["id"]))
    if entitlement is None:
        return _json_error("Unable to load entitlement for this account.", 404)
    return JSONResponse({"ok": True, "entitlement": entitlement})


async def create_checkout_session(request: Request) -> JSONResponse:
    if not STRIPE_SECRET_KEY:
        return _json_error("Stripe is not configured on this server.", 503)

    try:
        user = _require_user(request)
    except PermissionError as exc:
        return _json_error(str(exc), 401)

    try:
        body = await request.json()
    except Exception:
        return _json_error("Request body must be valid JSON.", 400)

    price_id = str(body.get("price_id", "")).strip()
    if not price_id:
        return _json_error("price_id is required.", 400)

    # Validate the price_id against the configured sets when they are populated.
    # This prevents users from triggering checkout with arbitrary price IDs.
    allowed_price_ids = STRIPE_CORE_PRICE_IDS | STRIPE_PRO_PRICE_IDS
    if allowed_price_ids and price_id not in allowed_price_ids:
        return _json_error("The requested price is not available.", 400)

    # Stripe requires absolute URLs; convert relative paths using the request base.
    base = str(request.base_url).rstrip("/")
    success_url = STRIPE_SUCCESS_URL if STRIPE_SUCCESS_URL.startswith("http") else base + STRIPE_SUCCESS_URL
    cancel_url = STRIPE_CANCEL_URL if STRIPE_CANCEL_URL.startswith("http") else base + STRIPE_CANCEL_URL

    # Build the Stripe Checkout Session parameters (form-encoded).
    params: list[tuple[str, str]] = [
        ("mode", "subscription"),
        ("line_items[0][price]", price_id),
        ("line_items[0][quantity]", "1"),
        ("success_url", success_url),
        ("cancel_url", cancel_url),
        ("client_reference_id", str(user["id"])),
    ]

    # Attach an existing Stripe customer or pre-fill the email field.
    existing_customer_id = str(user.get("stripe_customer_id") or "").strip()
    if existing_customer_id:
        params.append(("customer", existing_customer_id))
    else:
        user_email = str(user.get("email") or "").strip()
        if user_email:
            params.append(("customer_email", user_email))

    # Embed the user id in metadata so the webhook can match the session.
    params.append(("metadata[user_id]", str(user["id"])))

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.stripe.com/v1/checkout/sessions",
                headers={"Authorization": "Bearer " + STRIPE_SECRET_KEY},
                data=params,
            )
    except httpx.RequestError as exc:
        return _json_error(f"Failed to reach Stripe: {exc}", 502)

    if response.status_code != 200:
        try:
            stripe_error = response.json().get("error", {}).get("message", "Unknown error")
        except Exception:
            stripe_error = "Unknown error"
        return _json_error(f"Stripe error: {stripe_error}", 502)

    try:
        session_data = response.json()
    except Exception:
        return _json_error("Invalid response from Stripe.", 502)

    checkout_url = session_data.get("url")
    if not checkout_url:
        return _json_error("Stripe did not return a checkout URL.", 502)

    return JSONResponse({"ok": True, "url": checkout_url})


async def stripe_webhook(request: Request) -> JSONResponse:
    if not STRIPE_WEBHOOK_SECRET:
        return _json_error("Stripe webhook is not configured.", 503)

    signature_header = request.headers.get("stripe-signature", "")
    if not signature_header:
        return _json_error("Missing Stripe signature header.", 400)

    payload_bytes = await request.body()
    if not _verify_stripe_signature(payload_bytes, signature_header):
        return _json_error("Invalid Stripe signature.", 400)

    try:
        event = json.loads(payload_bytes.decode("utf-8"))
    except UnicodeDecodeError:
        return _json_error("Invalid encoding in Stripe payload.", 400)
    except json.JSONDecodeError:
        return _json_error("Malformed JSON in Stripe payload.", 400)

    event_type = str(event.get("type", "")).strip()
    data_object = event.get("data", {}).get("object", {})
    if not isinstance(data_object, dict):
        return _json_error("Invalid Stripe event data.", 400)

    if event_type == "checkout.session.completed":
        result = _handle_stripe_checkout_completed(data_object)
    elif event_type in {"customer.subscription.created", "customer.subscription.updated"}:
        result = _handle_stripe_subscription_event(data_object)
    elif event_type == "customer.subscription.deleted":
        result = _handle_stripe_subscription_deleted(data_object)
    elif event_type == "invoice.paid":
        result = _handle_stripe_invoice_event(data_object, paid=True)
    elif event_type == "invoice.payment_failed":
        result = _handle_stripe_invoice_event(data_object, paid=False)
    else:
        return JSONResponse({"ok": True, "ignored": True, "eventType": event_type})

    if not result.get("updated"):
        return JSONResponse(
            {"ok": True, "eventType": event_type, "result": result, "applied": False}
        )
    return JSONResponse({"ok": True, "eventType": event_type, "result": result})


def _html_file(path: Path) -> FileResponse:
    if not path.exists():
        raise FileNotFoundError(path)
    return FileResponse(path)


async def landing(_: Request) -> FileResponse:
    return _html_file(BASE_DIR / "index.html")


async def signup(_: Request) -> FileResponse:
    return _html_file(BASE_DIR / "signup.html")


async def resources(_: Request) -> FileResponse:
    return _html_file(BASE_DIR / "resources.html")


async def student_dashboard(_: Request) -> FileResponse:
    return _html_file(DIST_DIR / "dashboard.html")


async def staff_dashboard(_: Request) -> FileResponse:
    return _html_file(DIST_DIR / "staff-dashboard.html")


async def admin_dashboard(_: Request) -> FileResponse:
    return _html_file(DIST_DIR / "admin-dashboard.html")


PWA_PUBLIC_DIR = BASE_DIR / "public"
PWA_ASSETS = {
    "manifest.json",
    "pwa.js",
    "service-worker.js",
    "offline.html",
    "icon-192.png",
    "icon-512.png",
    "icon-512-maskable.png",
    "apple-touch-icon.png",
}


async def pwa_asset(request: Request) -> Response:
    name = request.path_params["name"]
    path = PWA_PUBLIC_DIR / name
    if name not in PWA_ASSETS or not path.exists():
        return Response("Not Found", status_code=404)
    return FileResponse(path)


async def root_redirect(_: Request) -> RedirectResponse:
    return RedirectResponse(f"/{STREAMLIT_BASE_PATH}/", status_code=307)


def _filtered_headers(headers: httpx.Headers) -> dict[str, str]:
    blocked = {"connection", "content-length", "content-encoding", "transfer-encoding"}
    return {key: value for key, value in headers.items() if key.lower() not in blocked}


async def proxy_streamlit_http(request: Request) -> Response:
    target_path = request.url.path
    query_string = request.url.query
    target_url = f"{STREAMLIT_HTTP_BASE}{target_path}"
    if query_string:
        target_url = f"{target_url}?{query_string}"

    request_body = await request.body()
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length"}
    }

    async with httpx.AsyncClient(follow_redirects=False, timeout=120) as client:
        upstream = await client.request(
            request.method,
            target_url,
            content=request_body,
            headers=headers,
        )
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=_filtered_headers(upstream.headers),
    )


async def proxy_streamlit_websocket(websocket: WebSocket) -> None:
    query = websocket.url.query
    target_url = f"{STREAMLIT_WS_BASE}{websocket.url.path}"
    if query:
        target_url = f"{target_url}?{query}"

    headers = {
        key: value
        for key, value in websocket.headers.items()
        if key.lower() not in {"host", "connection", "upgrade", "sec-websocket-key", "sec-websocket-version", "sec-websocket-extensions"}
    }

    async with websockets.connect(target_url, additional_headers=headers) as upstream:
        await websocket.accept()

        async def client_to_upstream() -> None:
            while True:
                message = await websocket.receive()
                message_type = message.get("type")
                if message_type == "websocket.disconnect":
                    break
                if message.get("text") is not None:
                    await upstream.send(message["text"])
                elif message.get("bytes") is not None:
                    await upstream.send(message["bytes"])

        async def upstream_to_client() -> None:
            async for message in upstream:
                if isinstance(message, bytes):
                    await websocket.send_bytes(message)
                else:
                    await websocket.send_text(message)

        tasks = [
            asyncio.create_task(client_to_upstream()),
            asyncio.create_task(upstream_to_client()),
        ]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        for task in done:
            if task.cancelled():
                continue
            exception = task.exception()
            if exception and not isinstance(exception, WebSocketDisconnect):
                raise exception

    with suppress(RuntimeError, WebSocketDisconnect):
        await websocket.close()


def _ensure_frontend_build() -> None:
    required_files = [
        DIST_DIR / "dashboard.html",
        DIST_DIR / "staff-dashboard.html",
        DIST_DIR / "admin-dashboard.html",
    ]
    missing = [str(path.name) for path in required_files if not path.exists()]
    if missing:
        raise RuntimeError(
            "Missing built frontend files: "
            + ", ".join(missing)
            + f". Run `npm run build` from {BASE_DIR} before starting the server."
        )


async def _wait_for_streamlit() -> None:
    health_url = f"{STREAMLIT_HTTP_BASE}/{STREAMLIT_BASE_PATH}/_stcore/health"
    async with httpx.AsyncClient(timeout=5) as client:
        for _ in range(40):
            try:
                response = await client.get(health_url)
                if response.is_success:
                    return
            except httpx.HTTPError:
                pass
            await asyncio.sleep(0.5)
    raise RuntimeError("Streamlit child server did not become ready.")


@asynccontextmanager
async def lifespan(app: Starlette):
    _ensure_frontend_build()

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "streamlit_app.py",
        "--server.port",
        str(STREAMLIT_PORT),
        "--server.address",
        STREAMLIT_HOST,
        "--server.headless",
        "true",
        "--server.baseUrlPath",
        STREAMLIT_BASE_PATH,
        "--browser.gatherUsageStats",
        "false",
    ]
    process = subprocess.Popen(
        command,
        cwd=str(BASE_DIR),
        env={**os.environ, "STREAMLIT_SERVER_HEADLESS": "true"},
    )
    app.state.streamlit_process = process
    try:
        await _wait_for_streamlit()
        yield
    finally:
        if process.poll() is None:
            process.terminate()
            with suppress(subprocess.TimeoutExpired):
                process.wait(timeout=10)
        if process.poll() is None:
            process.kill()


routes = [
    Route("/", landing),
    Route("/index.html", landing),
    Route("/signup.html", signup),
    Route("/resources.html", resources),
    Route("/dashboard.html", student_dashboard),
    Route("/staff-dashboard.html", staff_dashboard),
    Route("/admin-dashboard.html", admin_dashboard),
    Route("/api/health", health),
    Route("/api/auth/session", get_session, methods=["GET"]),
    Route("/api/auth/register", register, methods=["POST"]),
    Route("/api/auth/login", login, methods=["POST"]),
    Route("/api/auth/logout", logout, methods=["POST"]),
    Route("/api/portal/student", student_portal, methods=["GET"]),
    Route("/api/portal/course-progress", sync_course_progress, methods=["POST"]),
    Route("/api/portal/staff", staff_portal, methods=["GET"]),
    Route("/api/portal/admin", admin_portal, methods=["GET"]),
    Route("/api/billing/entitlement", current_entitlement, methods=["GET"]),
    Route("/api/billing/create-checkout-session", create_checkout_session, methods=["POST"]),
    Route("/api/billing/stripe/webhook", stripe_webhook, methods=["POST"]),
    Route(f"/{STREAMLIT_BASE_PATH}", root_redirect),
    Route(f"/{STREAMLIT_BASE_PATH}/{{path:path}}", proxy_streamlit_http, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]),
    WebSocketRoute(f"/{STREAMLIT_BASE_PATH}/{{path:path}}", proxy_streamlit_websocket),
    Mount("/compiled", app=StaticFiles(directory=str(COMPILED_DIR)), name="compiled"),
    Mount("/assets", app=StaticFiles(directory=str(ASSET_DIR)), name="assets"),
    Mount("/css", app=StaticFiles(directory=str(CSS_DIR)), name="css"),
    Mount("/portal-data", app=StaticFiles(directory=str(PORTAL_DATA_DIR)), name="portal-data"),
    Route("/{name:str}", pwa_asset, methods=["GET"], name="pwa-asset"),
]

app = Starlette(debug=False, routes=routes, lifespan=lifespan)
