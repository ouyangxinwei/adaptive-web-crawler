from scrapling.fetchers import Fetcher

from backend.app.config import settings


class ScraplingFetchError(RuntimeError):
    """Raised when a Scrapling request fails."""


class ScraplingFetcherAdapter:
    """
    Unified adapter for Scrapling's basic Fetcher.
    """

    def __init__(self):
        self.timeout = settings.request_timeout
        self.retries = settings.max_retries

    def fetch(self, url: str):
        """
        Fetch a webpage and return the parsed page object.
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")

        if not url.startswith(("http://", "https://")):
            raise ValueError("Only HTTP and HTTPS URLs are supported")

        try:
            page = Fetcher.get(
                url,
                timeout=self.timeout,
                retries=self.retries,
            )

            if page.status >= 400:
                raise ScraplingFetchError(
                    f"HTTP error {page.status} while fetching: {url}"
                )

            return page

        except ScraplingFetchError:
            raise
        except Exception as exc:
            raise ScraplingFetchError(
                f"Failed to fetch {url}: {exc}"
            ) from exc

    def extract_first(self, page, selector: str, default=None):
        """
        Extract the first matching element.
        """
        if not selector or not selector.strip():
            raise ValueError("CSS selector cannot be empty")

        result = page.css(selector).get()

        if result is None:
            return default

        return result

    def extract_all(self, page, selector: str) -> list:
        """
        Extract all matching elements.
        """
        if not selector or not selector.strip():
            raise ValueError("CSS selector cannot be empty")

        return page.css(selector).getall()
