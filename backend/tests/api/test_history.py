"""Tests for GET /api/v1/history — Phase 1 stub."""

from __future__ import annotations


class TestHistoryEndpoint:
    """Tests for the paginated history endpoint."""

    def test_history_returns_200(self, client):
        assert client.get("/api/v1/history").status_code == 200

    def test_history_default_pagination(self, client):
        data = client.get("/api/v1/history").json()
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert data["total"] == 0
        assert data["items"] == []

    def test_history_custom_page_size(self, client):
        data = client.get("/api/v1/history?page=1&page_size=10").json()
        assert data["page_size"] == 10

    def test_history_custom_page(self, client):
        data = client.get("/api/v1/history?page=3&page_size=5").json()
        assert data["page"] == 3
        assert data["page_size"] == 5

    def test_history_page_size_too_large_returns_422(self, client):
        response = client.get("/api/v1/history?page_size=101")
        assert response.status_code == 422

    def test_history_page_zero_returns_422(self, client):
        response = client.get("/api/v1/history?page=0")
        assert response.status_code == 422

    def test_history_negative_page_returns_422(self, client):
        response = client.get("/api/v1/history?page=-1")
        assert response.status_code == 422

    def test_history_response_shape(self, client):
        data = client.get("/api/v1/history").json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

    def test_history_empty_total_pages_is_zero(self, client):
        data = client.get("/api/v1/history").json()
        assert data["total_pages"] == 0

    def test_history_items_is_list(self, client):
        data = client.get("/api/v1/history").json()
        assert isinstance(data["items"], list)
