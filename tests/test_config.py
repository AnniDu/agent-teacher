from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.config import load_settings


class ConfigTest(unittest.TestCase):
    def test_loads_gemini_settings_from_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "GEMINI_API_KEY=file-key\nGEMINI_MODEL=gemini-test-model\n"
            )

            with patch.dict(os.environ, {}, clear=True):
                settings = load_settings(root)

            self.assertEqual(settings.gemini_api_key, "file-key")
            self.assertEqual(settings.gemini_model, "gemini-test-model")

    def test_exported_environment_overrides_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "GEMINI_API_KEY=file-key\nGEMINI_MODEL=gemini-test-model\n"
            )

            with patch.dict(
                os.environ,
                {"GEMINI_API_KEY": "exported-key", "GEMINI_MODEL": "exported-model"},
                clear=True,
            ):
                settings = load_settings(root)

            self.assertEqual(settings.gemini_api_key, "exported-key")
            self.assertEqual(settings.gemini_model, "exported-model")


if __name__ == "__main__":
    unittest.main()
