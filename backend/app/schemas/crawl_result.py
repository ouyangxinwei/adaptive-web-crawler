
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CrawlResultResponse(BaseModel):
    id: int
    crawl_run_id: int
    url: str
    title: str | None
    data: dict[str, Any]
    content: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
