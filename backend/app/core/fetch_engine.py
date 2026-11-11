
import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.core.fetcher_adapter import ScraplingFetcherAdapter
from backend.app.core.browser_fetcher_adapter import (
    ScraplingBrowserFetcherAdapter,
)
from backend.app.models import CrawlRun, CrawlResult
from backend.app.schemas.fetch_result import FetchResult


class FetchEngine:
    """
    Unified entry point for webpage fetching operations.
    Supports database persistence of crawl runs and results.
    """

    def __init__(self):
        self.http_fetcher = ScraplingFetcherAdapter()
        self.browser_fetcher = ScraplingBrowserFetcherAdapter()

    def fetch(
        self,
        db: Session,
        source_id: int,
        url: str,
        mode: str | None = None,
        wait_selector: str | None = None,
        task_id: int | None = None,
    ) -> FetchResult:
        """
        Fetch a webpage and persist its execution record and result.
        """

        selected_mode = (
            mode or settings.default_fetcher
        ).strip().lower()

        if selected_mode not in ("fetcher", "browser"):
            raise ValueError(
                f"Unsupported fetch mode: {selected_mode}"
            )

        started_at = datetime.now(timezone.utc)

        # Create and persist the crawl execution record.
        crawl_run = CrawlRun(
            source_id=source_id,
            task_id=task_id,
            status="running",
            fetch_mode=selected_mode,
            started_at=started_at,
            items_count=0,
        )

        db.add(crawl_run)
        db.commit()
        db.refresh(crawl_run)

        # Preserve the ID before any possible rollback.
        crawl_run_id = crawl_run.id

        start_time = time.perf_counter()

        try:
            if selected_mode == "fetcher":
                page = self.http_fetcher.fetch(url)
            else:
                page = self.browser_fetcher.fetch(
                    url,
                    wait_selector=wait_selector,
                )

            elapsed_ms = (
                time.perf_counter() - start_time
            ) * 1000

            fetched_at = datetime.now(timezone.utc)
            title = page.css("title::text").get()
            html = page.html_content or ""

            # Save the fetched webpage.
            crawl_result = CrawlResult(
                crawl_run_id=crawl_run_id,
                url=url,
                title=title,
                data={
                    "status_code": page.status,
                    "mode": selected_mode,
                    "elapsed_ms": elapsed_ms,
                    "fetched_at": fetched_at.isoformat(),
                },
                content=html,
            )

            db.add(crawl_result)

            crawl_run.status = "success"
            crawl_run.finished_at = fetched_at
            crawl_run.items_count = 1
            crawl_run.error_message = None

            db.commit()
            db.refresh(crawl_result)

            return FetchResult(
                success=True,
                url=url,
                status_code=page.status,
                title=title,
                html=html,
                mode=selected_mode,
                elapsed_ms=elapsed_ms,
                fetched_at=fetched_at,
                crawl_run_id=crawl_run_id,
                saved_result_id=crawl_result.id,
            )

        except Exception as exc:
            elapsed_ms = (
                time.perf_counter() - start_time
            ) * 1000

            db.rollback()

            # Preserve the execution record as a failed run.
            try:
                crawl_run = db.get(CrawlRun, crawl_run_id)

                if crawl_run is not None:
                    finished_at = datetime.now(timezone.utc)
                    crawl_run.status = "failed"
                    crawl_run.finished_at = finished_at
                    crawl_run.items_count = 0
                    crawl_run.error_message = str(exc)
                    db.commit()

            except Exception:
                db.rollback()
                raise

            return FetchResult(
                success=False,
                url=url,
                status_code=None,
                title=None,
                html="",
                mode=selected_mode,
                elapsed_ms=elapsed_ms,
                fetched_at=datetime.now(timezone.utc),
                error=str(exc),
                crawl_run_id=crawl_run_id,
            )
