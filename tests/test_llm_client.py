from __future__ import annotations

import unittest
from unittest.mock import patch

import requests

from agent_teacher.llm_client import GeminiClient, LLMError


class GeminiClientRetryTest(unittest.TestCase):
    def test_generate_retries_transient_http_failure_then_succeeds(self) -> None:
        client = GeminiClient(api_key="key", model="model")
        transient_response = _response(status_code=503, reason="Service Unavailable")
        success_response = _response(data=_gemini_response("ok"))

        with (
            patch(
                "agent_teacher.llm_client.requests.post",
                side_effect=[transient_response, success_response],
            ) as post,
            patch("agent_teacher.llm_client.time.sleep") as sleep,
            patch("agent_teacher.llm_client.print") as print_,
        ):
            result = client.generate("prompt")

        self.assertEqual(result, "ok")
        self.assertEqual(post.call_count, 2)
        sleep.assert_called_once_with(30)
        print_.assert_called_once()
        self.assertIn("503 Service Unavailable", print_.call_args.args[0])
        self.assertIn("attempt 2/5", print_.call_args.args[0])

    def test_generate_does_not_retry_permanent_http_failure(self) -> None:
        client = GeminiClient(api_key="key", model="model")
        permanent_response = _response(status_code=400, reason="Bad Request")

        with (
            patch("agent_teacher.llm_client.requests.post", return_value=permanent_response) as post,
            patch("agent_teacher.llm_client.time.sleep") as sleep,
        ):
            with self.assertRaises(LLMError):
                client.generate("prompt")

        self.assertEqual(post.call_count, 1)
        sleep.assert_not_called()

    def test_generate_raises_after_retry_limit(self) -> None:
        client = GeminiClient(api_key="key", model="model")
        transient_response = _response(status_code=503, reason="Service Unavailable")

        with (
            patch("agent_teacher.llm_client.requests.post", return_value=transient_response) as post,
            patch("agent_teacher.llm_client.time.sleep") as sleep,
            patch("agent_teacher.llm_client.print"),
        ):
            with self.assertRaises(LLMError):
                client.generate("prompt")

        self.assertEqual(post.call_count, 5)
        self.assertEqual(sleep.call_count, 4)

    def test_generate_retries_timeout_then_succeeds(self) -> None:
        client = GeminiClient(api_key="key", model="model")
        success_response = _response(data=_gemini_response("ok"))

        with (
            patch(
                "agent_teacher.llm_client.requests.post",
                side_effect=[requests.Timeout("timed out"), success_response],
            ) as post,
            patch("agent_teacher.llm_client.time.sleep") as sleep,
            patch("agent_teacher.llm_client.print"),
        ):
            result = client.generate("prompt")

        self.assertEqual(result, "ok")
        self.assertEqual(post.call_count, 2)
        sleep.assert_called_once_with(30)


class _FakeResponse:
    def __init__(
        self,
        data: dict[str, object] | None = None,
        status_code: int | None = None,
        reason: str | None = None,
    ) -> None:
        self._data = data or {}
        self.status_code = status_code
        self.reason = reason

    def raise_for_status(self) -> None:
        if self.status_code and self.status_code >= 400:
            raise requests.HTTPError(response=self)

    def json(self) -> dict[str, object]:
        return self._data


def _response(
    data: dict[str, object] | None = None,
    status_code: int | None = None,
    reason: str | None = None,
) -> _FakeResponse:
    return _FakeResponse(data=data, status_code=status_code, reason=reason)


def _gemini_response(text: str) -> dict[str, object]:
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


if __name__ == "__main__":
    unittest.main()
