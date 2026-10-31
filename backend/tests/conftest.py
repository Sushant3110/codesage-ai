"""Pytest configuration and shared fixtures for CodeSage AI backend tests.

External services (MongoDB, ChromaDB, Gemini) are mocked by default.
Tests that need real services are marked @pytest.mark.integration and
are skipped unless INTEGRATION_TESTS=1 is set in the environment.

Mocking strategy:
  The lifespan in app/main.py uses `import pymongo` and `import chromadb`
  (via importlib) inside the async context manager. We inject lightweight
  fake modules into sys.modules BEFORE the lifespan runs (i.e., before
  TestClient.__enter__). This avoids needing the real packages installed.

  We also patch `app.main.get_settings` so the app uses test defaults
  without reading any real .env file.
"""

from __future__ import annotations

import os
import sys
import types
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings

# ---------------------------------------------------------------------------
# Test settings — safe defaults, no real secrets
# ---------------------------------------------------------------------------


def _test_settings() -> Settings:
    return Settings(
        gemini_api_key="test-key-placeholder",
        mongodb_uri="mongodb://localhost:27017",
        mongodb_db_name="codesage_test",
        chroma_persist_dir="/tmp/codesage_test_chroma",
        log_level="WARNING",
        cors_origins="http://localhost:5173",
    )


# ---------------------------------------------------------------------------
# Lightweight fake modules for heavy optional deps
# ---------------------------------------------------------------------------


def _make_fake_pymongo() -> types.ModuleType:
    """Fake pymongo that never opens a real TCP connection."""
    mod = types.ModuleType("pymongo")
    mock_db = MagicMock()
    mock_client = MagicMock()
    mock_client.admin.command.return_value = {"ok": 1}
    mock_client.__getitem__ = MagicMock(return_value=mock_db)
    mod.MongoClient = MagicMock(return_value=mock_client)  # type: ignore[attr-defined]
    return mod


def _make_fake_chromadb() -> types.ModuleType:
    """Fake chromadb that never reads from disk."""
    mod = types.ModuleType("chromadb")
    mock_collection = MagicMock()
    mock_collection.count.return_value = 0
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mod.PersistentClient = MagicMock(return_value=mock_client)  # type: ignore[attr-defined]
    mod.config = MagicMock()
    mod.utils = MagicMock()
    return mod


# ---------------------------------------------------------------------------
# App fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def app_with_mocked_deps():
    """FastAPI TestClient with all external dependencies mocked.

    Yields (client, app).
    """
    # Save originals (may be None if not installed)
    orig_pymongo = sys.modules.get("pymongo")
    orig_chromadb = sys.modules.get("chromadb")

    # Inject fakes BEFORE importing create_app so the lifespan picks them up.
    sys.modules["pymongo"] = _make_fake_pymongo()
    sys.modules["chromadb"] = _make_fake_chromadb()

    # Clear settings cache so our overrides take effect.
    get_settings.cache_clear()

    try:
        # Import here (after sys.modules is patched) to avoid any side effects
        # from the module-level `app = create_app()` in main.py picking up real deps.
        # The module-level call does NOT run the lifespan — only TestClient does.
        from app.main import create_app

        # Patch both the re-export in main and the original in config
        # (lifespan calls get_settings() which resolves via app.config)
        test_settings = _test_settings()
        with (
            patch("app.main.get_settings", return_value=test_settings),
            patch("app.config.get_settings", return_value=test_settings),
        ):
            test_app = create_app()
            test_app.state.settings = test_settings
            test_app.dependency_overrides[get_settings] = lambda: test_settings

            # TestClient.__enter__ triggers the lifespan startup.
            with TestClient(test_app, raise_server_exceptions=False) as client:
                yield client, test_app
    finally:
        # Restore sys.modules
        if orig_pymongo is None:
            sys.modules.pop("pymongo", None)
        else:
            sys.modules["pymongo"] = orig_pymongo
        if orig_chromadb is None:
            sys.modules.pop("chromadb", None)
        else:
            sys.modules["chromadb"] = orig_chromadb
        get_settings.cache_clear()


@pytest.fixture()
def client(app_with_mocked_deps):
    """Convenience fixture: just the TestClient."""
    test_client, _ = app_with_mocked_deps
    return test_client


@pytest.fixture()
def test_app(app_with_mocked_deps):
    """Convenience fixture: just the app instance."""
    _, _app = app_with_mocked_deps
    return _app


# ---------------------------------------------------------------------------
# Integration marker — skip unless explicitly enabled
# ---------------------------------------------------------------------------


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: mark test as requiring live external services (MongoDB, ChromaDB).",
    )


def pytest_collection_modifyitems(config, items):
    if not os.environ.get("INTEGRATION_TESTS"):
        skip_integration = pytest.mark.skip(reason="Set INTEGRATION_TESTS=1 to run integration tests.")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
