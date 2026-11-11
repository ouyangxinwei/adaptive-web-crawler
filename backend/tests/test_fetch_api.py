
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.routes.fetch import fetch_engine
from backend.app.schemas.fetch_result import FetchResult


client = TestClient(app)


def make_result(url: str, mode: str) -> FetchResult:
    return FetchResult(
        success=True,
        url=url,
        status_code=200,
        title="Quotes to Scrape",
        html="<html><title>Quotes to Scrape</title></html>",
        mode=mode,
        elapsed_ms=100.0,
        fetched_at=datetime.now(timezone.utc),
        error=None,
    )


def test_fetch_api_http_mode(monkeypatch):
    def fake_fetch(url, mode=None, wait_selector=None):
        return make_result(url, mode or "fetcher")

    monkeypatch.setattr(fetch_engine, "fetch", fake_fetch)

    response = client.post(
        "/api/v1/fetch",
        json={
            "url": "https://quotes.toscrape.com/",
            "mode": "fetcher",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["status_code"] == 200
    assert data["title"] == "Quotes to Scrape"
    assert data["mode"] == "fetcher"


def test_fetch_api_browser_mode(monkeypatch):
    captured = {}

    def fake_fetch(url, mode=None, wait_selector=None):
        captured["url"] = url
        captured["mode"] = mode
        captured["wait_selector"] = wait_selector
        return make_result(url, mode)

    monkeypatch.setattr(fetch_engine, "fetch", fake_fetch)

    response = client.post(
        "/api/v1/fetch",
        json={
            "url": "https://quotes.toscrape.com/js-delayed/",
            "mode": "browser",
            "wait_selector": "div.quote",
        },
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["mode"] == "browser"
    assert captured["wait_selector"] == "div.quote"


def test_fetch_api_default_mode(monkeypatch):
    def fake_fetch(url, mode=None, wait_selector=None):
        return make_result(url, mode or "fetcher")

    monkeypatch.setattr(fetch_engine, "fetch", fake_fetch)

    response = client.post(
        "/api/v1/fetch",
        json={
            "url": "https://quotes.toscrape.com/",
        },
    )

    assert response.status_code == 200
    assert response.json()["mode"] == "fetcher"


def test_fetch_api_invalid_mode():
    response = client.post(
        "/api/v1/fetch",
        json={
            "url": "https://quotes.toscrape.com/",
            "mode": "unknown",
        },
    )

    assert response.status_code == 422


def test_fetch_api_invalid_url():
    response = client.post(
        "/api/v1/fetch",
        json={
            "url": "ftp://example.com",
        },
    )

    assert response.status_code == 422


def test_fetch_api_empty_url():
    response = client.post(
        "/api/v1/fetch",
        json={
            "url": "",
        },
    )

    assert response.status_code == 422
