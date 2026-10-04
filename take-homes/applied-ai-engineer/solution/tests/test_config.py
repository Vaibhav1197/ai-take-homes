"""Unit tests for config.py -- env-driven configuration."""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from solution.pipeline.config import load_config


class TestLoadConfig(unittest.TestCase):
    def test_local_engine_requires_explicit_weights_but_no_api_key(self) -> None:
        with patch.dict("os.environ", {"PIPELINE_JUDGE": "local"}, clear=True):
            with self.assertRaisesRegex(ValueError, "PIPELINE_LOCAL_MODEL_PATH"):
                load_config()
        with patch.dict("os.environ", {"PIPELINE_JUDGE": "local", "PIPELINE_LOCAL_MODEL_PATH": "models/qwen"}, clear=True):
            cfg = load_config()
        self.assertEqual(cfg.local_model_path, Path("models/qwen"))
        self.assertEqual(cfg.llm_timeout_seconds, 300)
        self.assertEqual(cfg.openai_model, "Qwen3.5-4B")
        self.assertEqual(cfg.local_engine, "openvino")

    def test_local_model_does_not_require_paid_key(self) -> None:
        with patch.dict("os.environ", {"PIPELINE_JUDGE": "llm",
                        "PIPELINE_LLM_API_URL": "http://127.0.0.1:8011/v1/chat/completions",
                        "PIPELINE_LLM_TIMEOUT_SECONDS": "300"}, clear=True):
            cfg = load_config()
        self.assertEqual(cfg.llm_timeout_seconds, 300)
        self.assertIn("127.0.0.1:8011", cfg.llm_api_url)

    def test_remote_cleartext_and_embedded_credentials_rejected(self) -> None:
        for url in ("http://example.com/v1/chat/completions", "https://user:secret@example.com/v1",
                    "https://example.com/v1?token=secret", "file:///tmp/model"):
            with self.subTest(url=url), patch.dict("os.environ", {"PIPELINE_LLM_API_URL": url}, clear=True):
                with self.assertRaises(ValueError):
                    load_config()

    def test_invalid_model_timeout_rejected(self) -> None:
        for value in ("0", "-1", "nan", "inf"):
            with self.subTest(value=value), patch.dict("os.environ", {"PIPELINE_LLM_TIMEOUT_SECONDS": value}, clear=True):
                with self.assertRaises(ValueError):
                    load_config()

    def test_defaults_point_at_repo_transcripts_and_data(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            cfg = load_config()
        self.assertTrue(str(cfg.transcripts_dir).endswith("transcripts"))
        self.assertTrue(str(cfg.existing_issues_path).endswith("existing_issues.json"))
        self.assertTrue(str(cfg.dev_labels_path).endswith("dev_labels.json"))

    def test_default_judge_is_heuristic(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            cfg = load_config()
        self.assertEqual(cfg.judge, "heuristic")

    def test_default_similarity_threshold_matches_dedup_default(self) -> None:
        from solution.pipeline.dedup import DEFAULT_SIMILARITY_THRESHOLD

        with patch.dict("os.environ", {}, clear=True):
            cfg = load_config()
        self.assertEqual(cfg.similarity_threshold, DEFAULT_SIMILARITY_THRESHOLD)

    def test_env_override_for_transcripts_dir(self) -> None:
        with patch.dict("os.environ", {"PIPELINE_TRANSCRIPTS_DIR": "/tmp/custom-transcripts"}, clear=True):
            cfg = load_config()
        self.assertEqual(cfg.transcripts_dir, Path("/tmp/custom-transcripts"))

    def test_env_override_for_similarity_threshold(self) -> None:
        with patch.dict("os.environ", {"PIPELINE_SIMILARITY_THRESHOLD": "0.35"}, clear=True):
            cfg = load_config()
        self.assertEqual(cfg.similarity_threshold, 0.35)

    def test_invalid_similarity_threshold_falls_back_to_default(self) -> None:
        from solution.pipeline.dedup import DEFAULT_SIMILARITY_THRESHOLD

        with patch.dict("os.environ", {"PIPELINE_SIMILARITY_THRESHOLD": "not-a-number"}, clear=True):
            cfg = load_config()
        self.assertEqual(cfg.similarity_threshold, DEFAULT_SIMILARITY_THRESHOLD)

    def test_judge_llm_requires_api_key(self) -> None:
        with patch.dict("os.environ", {"PIPELINE_JUDGE": "llm"}, clear=True):
            with self.assertRaises(ValueError):
                load_config()

    def test_judge_llm_succeeds_with_api_key(self) -> None:
        with patch.dict(
            "os.environ", {"PIPELINE_JUDGE": "llm", "OPENAI_API_KEY": "sk-test"}, clear=True
        ):
            cfg = load_config()
        self.assertEqual(cfg.judge, "llm")

    def test_invalid_judge_value_raises(self) -> None:
        with patch.dict("os.environ", {"PIPELINE_JUDGE": "magic8ball"}, clear=True):
            with self.assertRaises(ValueError):
                load_config()

    def test_openai_model_default_and_override(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            cfg = load_config()
        self.assertEqual(cfg.openai_model, "gpt-4o-mini")
        with patch.dict("os.environ", {"PIPELINE_OPENAI_MODEL": "gpt-4o"}, clear=True):
            cfg = load_config()
        self.assertEqual(cfg.openai_model, "gpt-4o")


if __name__ == "__main__":
    unittest.main()
