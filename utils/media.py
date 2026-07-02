"""Shared media helpers for Streamlit pages and curriculum modules."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
MEDIA_REGISTRY_PATH = REPO_ROOT / "knowledge" / "media" / "media_registry.json"
MEDIA_FIELDS = (
    "hero_image",
    "thumbnail",
    "video_url",
    "caption",
    "credit",
    "source",
    "video_caption",
)


def _blank_media_entry() -> dict[str, Any]:
    return {
        "hero_image": None,
        "thumbnail": None,
        "video_url": None,
        "caption": "",
        "credit": "",
        "source": "",
        "video_caption": "",
    }


@lru_cache(maxsize=1)
def load_media_registry() -> dict[str, dict[str, dict[str, Any]]]:
    registry: dict[str, dict[str, dict[str, Any]]] = {
        "defaults": {
            "pages": _blank_media_entry(),
            "modules": _blank_media_entry(),
        },
        "pages": {},
        "modules": {},
    }

    try:
        raw_registry = json.loads(MEDIA_REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return registry

    if not isinstance(raw_registry, dict):
        return registry

    defaults = raw_registry.get("defaults", {})
    if isinstance(defaults, dict):
        for scope in ("pages", "modules"):
            registry["defaults"][scope] = _normalize_media_entry(defaults.get(scope))

    for scope in ("pages", "modules"):
        raw_scope = raw_registry.get(scope, {})
        if not isinstance(raw_scope, dict):
            continue
        registry[scope] = {
            str(key): _normalize_media_entry(value)
            for key, value in raw_scope.items()
        }

    return registry


def _normalize_media_entry(entry: Any) -> dict[str, Any]:
    normalized = _blank_media_entry()
    if not isinstance(entry, dict):
        return normalized

    for field in MEDIA_FIELDS:
        value = entry.get(field)
        if value is None:
            continue
        text = str(value).strip()
        if field in {"hero_image", "thumbnail", "video_url"}:
            normalized[field] = text or None
        else:
            normalized[field] = text
    return normalized


@lru_cache(maxsize=32)
def _read_markdown_document_cached(path_str: str) -> tuple[dict[str, Any], str, bool]:
    try:
        raw_text = Path(path_str).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return {}, "", True

    frontmatter, content = _split_frontmatter(raw_text)
    return frontmatter, content.strip(), False


def read_markdown_document(path: str | Path) -> tuple[dict[str, Any], str, bool]:
    return _read_markdown_document_cached(str(path))


def _split_frontmatter(raw_text: str) -> tuple[dict[str, Any], str]:
    stripped = raw_text.lstrip()
    if not stripped.startswith("---"):
        return {}, raw_text

    lines = stripped.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, raw_text

    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break

    if closing_index is None:
        return {}, raw_text

    metadata: dict[str, Any] = {}
    for line in lines[1:closing_index]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            continue
        metadata[key] = _coerce_frontmatter_value(value)

    content = "\n".join(lines[closing_index + 1 :])
    return metadata, content


def _coerce_frontmatter_value(value: str) -> Any:
    text = value.strip()
    if not text:
        return None
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()
    lowered = text.lower()
    if lowered in {"null", "none"}:
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return text


def get_media_entry(
    scope: str,
    key: str,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_media_registry()
    defaults = registry.get("defaults", {}).get(scope, _blank_media_entry())
    scoped_entries = registry.get(scope, {})
    entry = scoped_entries.get(key, {})
    merged = {**defaults, **entry}
    if overrides:
        merged.update(
            {
                field: value
                for field, value in _normalize_media_entry(overrides).items()
                if value not in (None, "")
            }
        )
    return merged


def render_page_media(page_key: str) -> None:
    render_media_block(
        get_media_entry("pages", page_key),
        missing_image_message="Visual placeholder: add a page hero image in knowledge/media/media_registry.json.",
        missing_video_message="Optional intro video not configured for this page yet.",
        show_empty_video_message=False,
    )


def render_module_media(module_id: str, frontmatter: dict[str, Any] | None = None) -> None:
    render_media_block(
        get_media_entry("modules", module_id, frontmatter),
        missing_image_message="Lesson visual placeholder: add a hero image in the media registry or markdown frontmatter.",
        missing_video_message="Lesson video slot ready: add a local MP4/WebM path or HTTPS video URL when available.",
        show_empty_video_message=True,
    )


def render_media_block(
    media_entry: dict[str, Any],
    *,
    missing_image_message: str,
    missing_video_message: str,
    show_empty_video_message: bool,
) -> None:
    hero_source = _resolve_media_source(media_entry.get("hero_image"))
    thumbnail_source = _resolve_media_source(media_entry.get("thumbnail"))
    image_source = hero_source or thumbnail_source
    caption = _build_caption_text(media_entry)

    if image_source:
        try:
            st.image(image_source, caption=caption or None, use_container_width=True)
        except Exception:
            st.info("The visual for this section could not be loaded right now.")
            if caption:
                st.caption(caption)
    else:
        st.info(missing_image_message)
        if caption:
            st.caption(caption)

    raw_video = media_entry.get("video_url")
    video_source = _resolve_media_source(raw_video)
    if video_source:
        try:
            st.video(video_source)
        except Exception:
            st.info("The video for this section could not be loaded right now.")
    elif raw_video or show_empty_video_message:
        st.info(missing_video_message)

    video_caption = str(media_entry.get("video_caption") or "").strip()
    if video_caption:
        st.caption(video_caption)


def _build_caption_text(media_entry: dict[str, Any]) -> str:
    parts = [
        str(media_entry.get("caption") or "").strip(),
        str(media_entry.get("credit") or "").strip(),
        str(media_entry.get("source") or "").strip(),
    ]
    return " • ".join(part for part in parts if part)


def _resolve_media_source(raw_value: Any) -> str | None:
    if raw_value is None:
        return None

    text = str(raw_value).strip()
    if not text:
        return None
    if _is_remote_url(text):
        return text

    candidate = Path(text)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate

    if candidate.is_file():
        return str(candidate)
    return None


def _is_remote_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
