
from scrapling.fetchers import StealthyFetcher

from backend.app.config import settings
from backend.app.core.fetcher_adapter import ScraplingFetchError


class ScraplingBrowserFetcherAdapter:
    """
    Browser-based fetch adapter using Scrapling StealthyFetcher.
    Supports JavaScript-rendered webpages.
    """

    def __init__(self):
        # Project settings use seconds; StealthyFetcher uses milliseconds.
        self.timeout = settings.request_timeout * 1000

    def fetch(self, url: str, wait_selector: str | None = None):
        """
        Open a browser, load the webpage and return the parsed page.
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")

        if not url.startswith(("http://", "https://")):
            raise ValueError("Only HTTP and HTTPS URLs are supported")

        try:
            options = {
                "timeout": self.timeout,
                "headless": True,
                "load_dom": True,
            }

            if wait_selector:
                options["wait_selector"] = wait_selector

            page = StealthyFetcher.fetch(url, **options)

            if page.status >= 400:
                raise ScraplingFetchError(
                    f"HTTP error {page.status} while fetching: {url}"
                )

            return page

        except ScraplingFetchError:
            raise
        except Exception as exc:
            raise ScraplingFetchError(
                f"Browser fetch failed for {url}: {exc}"
            ) from exc

    def extract_first(self, page, selector: str, default=None):
        """Extract the first matching element."""
        if not selector or not selector.strip():
            raise ValueError("CSS selector cannot be empty")

        result = page.css(selector).get()

        if result is None:
            return default

        return result

    def extract_all(self, page, selector: str) -> list:
        """Extract all matching elements."""
        if not selector or not selector.strip():
            raise ValueError("CSS selector cannot be empty")

        return page.css(selector).getall()
