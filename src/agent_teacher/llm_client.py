from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any

import requests


class LLMError(RuntimeError):
    pass


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
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise LLMError(f"Gemini request failed: {exc}") from exc

        try:
            parts = data["candidates"][0]["content"]["parts"]
            return "".join(part.get("text", "") for part in parts).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Unexpected Gemini response shape: {data}") from exc


def default_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    if provider == "gemini":
        return GeminiClient()
    raise LLMError(f"Unsupported LLM_PROVIDER: {provider}")

