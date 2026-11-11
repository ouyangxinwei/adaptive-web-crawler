
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CrawlRunResponse(BaseModel):
    id: int
    source_id: int
    task_id: int | None
    status: str
    fetch_mode: str
    started_at: datetime | None
    finished_at: datetime | None
    items_count: int = Field(ge=0)
    error_message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
