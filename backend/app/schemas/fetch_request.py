
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class FetchRequest(BaseModel):
    """Request schema for webpage fetching."""

    url: str = Field(
        ...,
        min_length=1,
        description="Target webpage URL",
    )

    mode: Literal["fetcher", "browser"] = Field(
        default="fetcher",
        description="Fetching mode",
    )

    wait_selector: str | None = Field(
        default=None,
        description="Optional CSS selector to wait for in browser mode",
    )

    source_id: int = Field(
        gt=0,
        description="Existing data source ID",
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        value = value.strip()

        if not value.startswith(("http://", "https://")):
            raise ValueError("Only HTTP and HTTPS URLs are supported")

        return value
