from __future__ import annotations

import os
import sys
import time
from abc import ABC, abstractmethod
from typing import Any

import requests


class LLMError(RuntimeError):
    pass


_MAX_ATTEMPTS = 5
_RETRY_DELAY_SECONDS = 30
_TRANSIENT_STATUS_CODES = {429, 500, 502, 503, 504}


class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class GeminiClient(LLMClient):
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL")
        if not self.api_key:
            raise LLMError("Missing GEMINI_API_KEY. Set it before running learn.")
        if not self.model:
            raise LLMError("Missing GEMINI_MODEL. Set it before running learn.")

    def generate(self, prompt: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        payload: dict[str, Any] = {"contents": [{"parts": [{"text": prompt}]}]}
        data = self._post_with_retries(url, payload)

        try:
            parts = data["candidates"][0]["content"]["parts"]
            return "".join(part.get("text", "") for part in parts).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Unexpected Gemini response shape: {data}") from exc

    def _post_with_retries(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            for attempt in range(1, _MAX_ATTEMPTS + 1):
                try:
                    response = requests.post(url, json=payload, timeout=60)
                    response.raise_for_status()
                    data = response.json()
                    if not isinstance(data, dict):
                        raise LLMError(f"Unexpected Gemini response shape: {data}")
                    return data
                except requests.RequestException as exc:
                    if attempt == _MAX_ATTEMPTS or not _is_transient_error(exc):
                        raise
                    _print_retry_message(exc, attempt + 1)
                    time.sleep(_RETRY_DELAY_SECONDS)
        except requests.RequestException as exc:
            raise LLMError(f"Gemini request failed: {exc}") from exc

        raise LLMError("Gemini request failed")


def default_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    if provider == "gemini":
        return GeminiClient()
    raise LLMError(f"Unsupported LLM_PROVIDER: {provider}")


def _is_transient_error(exc: requests.RequestException) -> bool:
    if isinstance(exc, (requests.ConnectionError, requests.Timeout)):
        return True
    response = getattr(exc, "response", None)
    status_code = getattr(response, "status_code", None)
    return status_code in _TRANSIENT_STATUS_CODES


def _print_retry_message(exc: requests.RequestException, next_attempt: int) -> None:
    print(
        f"LLM request failed ({_format_request_error(exc)}). "
        f"Retrying in {_RETRY_DELAY_SECONDS} seconds... "
        f"(attempt {next_attempt}/{_MAX_ATTEMPTS})",
        file=sys.stderr,
    )


def _format_request_error(exc: requests.RequestException) -> str:
    response = getattr(exc, "response", None)
    status_code = getattr(response, "status_code", None)
    reason = getattr(response, "reason", None)
    if status_code and reason:
        return f"{status_code} {reason}"
    if status_code:
        return str(status_code)
    return str(exc)
