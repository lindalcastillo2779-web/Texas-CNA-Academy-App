"""
LLM provider adapter
====================
Supports OpenAI (default) and Azure OpenAI via environment variables.

Environment variables
---------------------
LLM_PROVIDER          : "OPENAI" (default) | "AZURE_OPENAI"

OpenAI
  OPENAI_API_KEY      : required
  OPENAI_MODEL        : optional, defaults to "gpt-4o-mini"

Azure OpenAI
  AZURE_OPENAI_KEY         : required
  AZURE_OPENAI_ENDPOINT    : required  (e.g. https://my-resource.openai.azure.com/)
  AZURE_OPENAI_DEPLOYMENT  : required  (deployment / model name)
  AZURE_OPENAI_API_VERSION : optional, defaults to "2024-02-01"
"""

import os

# ─────────────────────────────────────────────────────────────────────────────
# Lazy import: openai is optional at import time so the rest of the app loads
# even when the package is not installed.
# ─────────────────────────────────────────────────────────────────────────────
try:
    import openai as _openai_module  # noqa: F401
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False


def _provider() -> str:
    return os.environ.get("LLM_PROVIDER", "OPENAI").upper().strip()


def _build_client():
    """Return a configured openai.OpenAI or openai.AzureOpenAI client."""
    if not _OPENAI_AVAILABLE:
        raise RuntimeError(
            "The 'openai' package is not installed. "
            "Run: pip install openai"
        )

    import openai  # local import after availability check

    provider = _provider()

    if provider == "AZURE_OPENAI":
        key      = os.environ.get("AZURE_OPENAI_KEY", "").strip()
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()
        version  = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01").strip()
        if not key or not endpoint:
            raise ValueError(
                "Azure OpenAI requires AZURE_OPENAI_KEY and "
                "AZURE_OPENAI_ENDPOINT environment variables."
            )
        return openai.AzureOpenAI(
            api_key=key,
            azure_endpoint=endpoint,
            api_version=version,
        )

    # Default: OpenAI
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is not set. "
            "Add it to your .env file or Render environment."
        )
    return openai.OpenAI(api_key=key)


def _model_name() -> str:
    """Return the model / deployment name for the configured provider."""
    provider = _provider()
    if provider == "AZURE_OPENAI":
        name = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "").strip()
        if not name:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT environment variable is not set.")
        return name
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()


def chat_completion(messages: list[dict], temperature: float = 0.3) -> str:
    """
    Send a list of OpenAI-format messages and return the reply string.

    Parameters
    ----------
    messages    : list of {"role": ..., "content": ...} dicts
    temperature : sampling temperature (lower = more factual)

    Returns
    -------
    str – the assistant's reply text

    Raises
    ------
    RuntimeError  if the openai package is missing
    ValueError    if required env vars are absent
    Exception     re-raised from the OpenAI SDK on API errors
    """
    client = _build_client()
    model  = _model_name()
    resp   = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""
