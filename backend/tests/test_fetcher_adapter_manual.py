from backend.app.core.fetcher_adapter import (
    ScraplingFetcherAdapter,
    ScraplingFetchError,
)


def main():
    adapter = ScraplingFetcherAdapter()

    url = "https://quotes.toscrape.com/"

    print("Testing Scrapling Fetcher Adapter")

    # Test normal fetching
    page = adapter.fetch(url)

    title = adapter.extract_first(page, "title::text")
    quotes = adapter.extract_all(page, "span.text::text")
    authors = adapter.extract_all(page, "small.author::text")

    print("\n[Normal Fetch]")
    print("HTTP Status:", page.status)
    print("Title:", title)
    print("Quotes:", len(quotes))
    print("Authors:", len(authors))

    assert page.status == 200
    assert title == "Quotes to Scrape"
    assert len(quotes) == 10
    assert len(authors) == 10

    # Test missing selector
    missing = adapter.extract_first(
        page,
        "div.non-existent",
        default="NOT FOUND",
    )

    assert missing == "NOT FOUND"
    print("\n[Missing Selector] Passed")

    # Test empty URL
    try:
        adapter.fetch("")
        raise AssertionError("Empty URL should be rejected")
    except ValueError:
        print("[Empty URL] Passed")

    # Test invalid URL scheme
    try:
        adapter.fetch("ftp://example.com")
        raise AssertionError("Invalid URL scheme should be rejected")
    except ValueError:
        print("[Invalid URL Scheme] Passed")

    print("\nAll adapter checks passed!")


if __name__ == "__main__":
    main()
