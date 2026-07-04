"""ASGI entrypoint for portal APIs, static assets, and Streamlit proxying."""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from contextlib import asynccontextmanager
from contextlib import suppress
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
    authenticate_user,
    build_admin_portal_payload,
    build_staff_portal_payload,
    build_student_portal_payload,
    create_or_claim_user_account,
    create_portal_session,
    delete_portal_session,
    get_portal_dashboard_path,
    get_portal_profile,
    get_user_by_session_token,
    init_db,
    is_admin_role,
    is_staff_role,
    normalize_email,
    normalize_role,
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
IS_PRODUCTION = os.environ.get("RENDER", "").lower() == "true"

init_db()


def _dashboard_target(role: str | None) -> str:
    return get_portal_dashboard_path(role)


def _role_requires_facility(role: str) -> bool:
    return role in {"staff", "admin"}


def _session_cookie_secure(request: Request) -> bool:
    return request.url.scheme == "https" or IS_PRODUCTION


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
            + ". Run `npm run build` before starting the server."
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
    Route("/api/portal/staff", staff_portal, methods=["GET"]),
    Route("/api/portal/admin", admin_portal, methods=["GET"]),
    Route(f"/{STREAMLIT_BASE_PATH}", root_redirect),
    Route(f"/{STREAMLIT_BASE_PATH}/{{path:path}}", proxy_streamlit_http, methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]),
    WebSocketRoute(f"/{STREAMLIT_BASE_PATH}/{{path:path}}", proxy_streamlit_websocket),
    Mount("/compiled", app=StaticFiles(directory=str(COMPILED_DIR)), name="compiled"),
    Mount("/assets", app=StaticFiles(directory=str(ASSET_DIR)), name="assets"),
    Mount("/css", app=StaticFiles(directory=str(CSS_DIR)), name="css"),
    Mount("/portal-data", app=StaticFiles(directory=str(PORTAL_DATA_DIR)), name="portal-data"),
]

app = Starlette(debug=False, routes=routes, lifespan=lifespan)
