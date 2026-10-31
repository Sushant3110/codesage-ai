"""Tests for GET /api/v1/health and GET /api/v1/ready endpoints."""

from __future__ import annotations


class TestHealthEndpoint:
    """Tests for GET /api/v1/health."""

    def test_health_returns_200(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_response_shape(self, client):
        data = client.get("/api/v1/health").json()
        assert "status" in data
        assert "version" in data

    def test_health_status_is_ok(self, client):
        data = client.get("/api/v1/health").json()
        assert data["status"] == "ok"

    def test_health_version_is_string(self, client):
        data = client.get("/api/v1/health").json()
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0


class TestReadinessEndpoint:
    """Tests for GET /api/v1/ready."""

    def test_ready_returns_json(self, client):
        response = client.get("/api/v1/ready")
        assert response.headers["content-type"].startswith("application/json")

    def test_ready_response_has_required_fields(self, client):
        data = client.get("/api/v1/ready").json()
        assert "status" in data
        assert "checks" in data
        checks = data["checks"]
        assert "mongodb" in checks
        assert "chromadb" in checks

    def test_ready_200_when_both_deps_ok(self, client, test_app):
        test_app.state.mongo_status = "ok"
        test_app.state.chroma_status = "ok"
        response = client.get("/api/v1/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"

    def test_ready_503_when_mongo_down(self, client, test_app):
        test_app.state.mongo_status = "error: connection refused"
        test_app.state.chroma_status = "ok"
        response = client.get("/api/v1/ready")
        assert response.status_code == 503
        assert response.json()["status"] == "not_ready"

    def test_ready_503_when_chroma_down(self, client, test_app):
        test_app.state.mongo_status = "ok"
        test_app.state.chroma_status = "error: directory not found"
        response = client.get("/api/v1/ready")
        assert response.status_code == 503
        assert response.json()["checks"]["chromadb"].startswith("error")

    def test_ready_503_when_both_down(self, client, test_app):
        test_app.state.mongo_status = "error: timeout"
        test_app.state.chroma_status = "error: timeout"
        response = client.get("/api/v1/ready")
        assert response.status_code == 503


class TestCapabilitiesEndpoint:
    """Tests for GET /api/v1/capabilities."""

    def test_capabilities_200(self, client):
        assert client.get("/api/v1/capabilities").status_code == 200

    def test_capabilities_response_shape(self, client):
        data = client.get("/api/v1/capabilities").json()
        assert "supported_languages" in data
        assert "llm_model" in data
        assert "static_analysis_tools" in data
        assert "rag_enabled" in data
        assert "rag_document_count" in data
        assert "max_code_size_bytes" in data

    def test_capabilities_supported_languages(self, client):
        data = client.get("/api/v1/capabilities").json()
        for expected in ("python", "java", "javascript", "typescript", "c", "cpp", "html", "css", "sql"):
            assert expected in data["supported_languages"]

    def test_capabilities_tools(self, client):
        data = client.get("/api/v1/capabilities").json()
        assert "ruff" in data["static_analysis_tools"]
        assert "bandit" in data["static_analysis_tools"]

    def test_capabilities_max_code_size(self, client):
        data = client.get("/api/v1/capabilities").json()
        assert data["max_code_size_bytes"] == 32768

    def test_capabilities_rag_disabled_when_no_docs(self, client):
        """With no RAG documents, rag_enabled should be False."""
        data = client.get("/api/v1/capabilities").json()
        # conftest mocks collection.count() to return 0
        assert data["rag_enabled"] is False
        assert data["rag_document_count"] == 0
