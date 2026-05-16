#!/usr/bin/env python3
"""Focused checks for canonical provider configuration."""
import ast
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src import provider_config


class ProviderConfigTests(unittest.TestCase):
    def test_public_defaults_are_unchanged(self):
        self.assertEqual(provider_config.DEFAULT_PROVIDER, "openai")
        self.assertEqual(
            provider_config.SUPPORTED_PROVIDERS,
            ("openai", "anthropic", "gemini"),
        )
        self.assertEqual(
            provider_config.VALID_LANGUAGES,
            ("mingrelian", "georgian", "english"),
        )
        self.assertEqual(
            provider_config.DEFAULT_MODEL_BY_PROVIDER,
            {
                "openai": "gpt-5.4-nano",
                "anthropic": "claude-sonnet-4-5-20250929",
                "gemini": "gemini-3.1-flash-lite-preview",
            },
        )

    def test_server_key_allowlist_is_centralized(self):
        self.assertEqual(
            provider_config.SERVER_KEY_MODELS,
            {
                "openai": frozenset({"gpt-5.4-nano"}),
                "gemini": frozenset({"gemini-3.1-flash-lite-preview"}),
            },
        )

        for provider, models in provider_config.SERVER_KEY_MODELS.items():
            self.assertIn(provider, provider_config.SUPPORTED_PROVIDERS)
            for model in models:
                self.assertTrue(
                    provider_config.is_server_key_model_allowed(provider, model)
                )

        self.assertFalse(
            provider_config.is_server_key_model_allowed(
                "anthropic",
                provider_config.DEFAULT_MODEL_BY_PROVIDER["anthropic"],
            )
        )

    def test_helpers_read_from_canonical_maps(self):
        for provider in provider_config.SUPPORTED_PROVIDERS:
            self.assertEqual(
                provider_config.get_default_model_for_provider(provider),
                provider_config.DEFAULT_MODEL_BY_PROVIDER[provider],
            )
            self.assertTrue(provider_config.get_api_key_env_var(provider))

        self.assertIsNone(provider_config.get_default_model_for_provider("unknown"))
        self.assertIsNone(provider_config.get_api_key_env_var("unknown"))

    def test_llm_client_uses_canonical_config(self):
        fake_dotenv = types.ModuleType("dotenv")
        fake_dotenv.load_dotenv = lambda *args, **kwargs: None

        with patch.dict(sys.modules, {"dotenv": fake_dotenv}):
            from src import llm_client

        self.assertIs(
            llm_client.DEFAULT_MODEL_BY_PROVIDER,
            provider_config.DEFAULT_MODEL_BY_PROVIDER,
        )
        self.assertIs(llm_client.LLMProvider, provider_config.LLMProvider)

    def test_api_imports_canonical_config(self):
        api_tree = ast.parse((PROJECT_ROOT / "fastapi_app" / "api.py").read_text())
        provider_config_imports = set()
        assigned_names = set()

        for node in ast.walk(api_tree):
            if isinstance(node, ast.ImportFrom) and node.module == "src.provider_config":
                provider_config_imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigned_names.add(target.id)

        self.assertGreaterEqual(
            provider_config_imports,
            {
                "DEFAULT_PROVIDER",
                "SERVER_KEY_MODELS",
                "SUPPORTED_PROVIDERS",
                "VALID_LANGUAGES",
                "get_default_model_for_provider",
                "is_server_key_model_allowed",
            },
        )
        self.assertTrue(
            {
                "SERVER_KEY_MODELS",
                "SUPPORTED_PROVIDERS",
                "VALID_LANGUAGES",
            }.isdisjoint(assigned_names)
        )


if __name__ == "__main__":
    unittest.main()
