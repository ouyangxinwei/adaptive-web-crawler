
import pytest

from backend.app.core.fetcher_adapter import (
    ScraplingFetcherAdapter,
    ScraplingFetchError,
)
from backend.app.core.browser_fetcher_adapter import (
    ScraplingBrowserFetcherAdapter,
)


TEST_URL = "https://quotes.toscrape.com/"
DYNAMIC_TEST_URL = "https://quotes.toscrape.com/js-delayed/"


def test_basic_fetcher():
    adapter = ScraplingFetcherAdapter()
    page = adapter.fetch(TEST_URL)

    assert page.status == 200
    assert adapter.extract_first(page, "title::text") == "Quotes to Scrape"
    assert len(adapter.extract_all(page, "span.text::text")) == 10


def test_basic_fetcher_missing_selector():
    adapter = ScraplingFetcherAdapter()
    page = adapter.fetch(TEST_URL)

    result = adapter.extract_first(
        page,
        "div.non-existent",
        default="NOT FOUND",
    )

    assert result == "NOT FOUND"


def test_browser_fetcher():
    adapter = ScraplingBrowserFetcherAdapter()
    page = adapter.fetch(
        DYNAMIC_TEST_URL,
        wait_selector="div.quote",
    )

    assert page.status == 200
    assert adapter.extract_first(page, "title::text") == "Quotes to Scrape"
    assert len(adapter.extract_all(page, "span.text::text")) == 10
    assert len(adapter.extract_all(page, "small.author::text")) == 10


@pytest.mark.parametrize(
    "url",
    [
        "",
        "ftp://example.com",
    ],
)
def test_invalid_urls(url):
    adapter = ScraplingFetcherAdapter()

    with pytest.raises(ValueError):
        adapter.fetch(url)


def test_browser_fetcher_invalid_url():
    adapter = ScraplingBrowserFetcherAdapter()

    with pytest.raises(ValueError):
        adapter.fetch("ftp://example.com")
