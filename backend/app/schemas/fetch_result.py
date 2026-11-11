
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class FetchResult(BaseModel):
    """Unified result returned by the fetching engine."""

    success: bool

    url: str
    status_code: int | None = None

    title: str | None = None
    html: str = ""

    mode: str

    elapsed_ms: float = Field(default=0.0, ge=0)

    fetched_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    error: str | None = None

    # Database persistence references
    crawl_run_id: int | None = None
    saved_result_id: int | None = None
