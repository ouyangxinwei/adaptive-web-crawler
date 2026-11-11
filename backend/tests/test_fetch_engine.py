
import pytest

from backend.app.core.fetch_engine import FetchEngine
from backend.app.schemas.fetch_result import FetchResult


TEST_URL = "https://quotes.toscrape.com/"
DYNAMIC_TEST_URL = "https://quotes.toscrape.com/js-delayed/"


def test_fetch_engine_http_mode():
    engine = FetchEngine()
    result = engine.fetch(TEST_URL, mode="fetcher")

    assert isinstance(result, FetchResult)
    assert result.success is True
    assert result.status_code == 200
    assert result.title == "Quotes to Scrape"
    assert result.mode == "fetcher"
    assert len(result.html) > 0
    assert result.elapsed_ms > 0
    assert result.error is None


def test_fetch_engine_browser_mode():
    engine = FetchEngine()
    result = engine.fetch(
        DYNAMIC_TEST_URL,
        mode="browser",
        wait_selector="div.quote",
    )

    assert result.success is True
    assert result.status_code == 200
    assert result.title == "Quotes to Scrape"
    assert result.mode == "browser"
    assert len(result.html) > 0
    assert result.error is None


def test_fetch_engine_default_mode():
    engine = FetchEngine()
    result = engine.fetch(TEST_URL)

    assert result.success is True
    assert result.status_code == 200
    assert result.mode == "fetcher"


def test_fetch_engine_invalid_mode():
    engine = FetchEngine()

    with pytest.raises(ValueError, match="Unsupported fetch mode"):
        engine.fetch(TEST_URL, mode="unknown")


def test_fetch_engine_failed_request():
    engine = FetchEngine()
    result = engine.fetch("ftp://example.com")

    assert result.success is False
    assert result.status_code is None
    assert result.html == ""
    assert result.mode == "fetcher"
    assert result.error is not None
    assert result.elapsed_ms >= 0
