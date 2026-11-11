
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class RuleCreate(BaseModel):
    source_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=200)
    selector: str = Field(min_length=1)
    selector_type: Literal["css", "xpath"] = "css"
    field_name: str = Field(min_length=1, max_length=200)
    extraction_config: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class RuleUpdate(BaseModel):
    source_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    selector: str | None = Field(default=None, min_length=1)
    selector_type: Literal["css", "xpath"] | None = None
    field_name: str | None = Field(default=None, min_length=1, max_length=200)
    extraction_config: dict[str, Any] | None = None
    is_active: bool | None = None


class RuleResponse(BaseModel):
    id: int
    source_id: int
    name: str
    selector: str
    selector_type: str
    field_name: str
    extraction_config: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
