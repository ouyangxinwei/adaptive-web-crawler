
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    source_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=200)
    schedule_type: Literal["manual", "interval", "cron"] = "manual"
    schedule_config: dict[str, Any] = Field(default_factory=dict)
    is_enabled: bool = True


class TaskUpdate(BaseModel):
    source_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    schedule_type: Literal["manual", "interval", "cron"] | None = None
    schedule_config: dict[str, Any] | None = None
    is_enabled: bool | None = None


class TaskResponse(BaseModel):
    id: int
    source_id: int
    name: str
    schedule_type: str
    schedule_config: dict[str, Any]
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    # Execution statistics
    last_run_at: datetime | None = None
    last_run_status: str | None = None
    total_runs: int = 0
    success_runs: int = 0
    failed_runs: int = 0

    model_config = ConfigDict(from_attributes=True)
