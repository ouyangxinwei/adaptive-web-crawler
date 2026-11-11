
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models import CrawlRun
from backend.app.schemas.crawl_run import CrawlRunResponse


router = APIRouter()


@router.get(
    "/crawl-runs",
    response_model=list[CrawlRunResponse],
    summary="Get crawl history",
)
def get_crawl_runs(
    source_id: int | None = Query(default=None, gt=0),
    task_id: int | None = Query(default=None, gt=0),
    status: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """Get crawl execution history with optional filters."""

    statement = select(CrawlRun)

    if source_id is not None:
        statement = statement.where(
            CrawlRun.source_id == source_id
        )

    if task_id is not None:
        statement = statement.where(
            CrawlRun.task_id == task_id
        )

    if status:
        statement = statement.where(
            CrawlRun.status == status
        )

    statement = (
        statement
        .order_by(CrawlRun.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get(
    "/crawl-runs/{run_id}",
    response_model=CrawlRunResponse,
    summary="Get crawl run details",
)
def get_crawl_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    """Get details of one crawl execution."""

    crawl_run = db.get(CrawlRun, run_id)

    if crawl_run is None:
        raise HTTPException(
            status_code=404,
            detail="Crawl run not found",
        )

    return crawl_run
