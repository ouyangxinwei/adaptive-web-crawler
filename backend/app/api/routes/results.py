
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models import CrawlResult, CrawlRun
from backend.app.schemas.crawl_result import CrawlResultResponse


router = APIRouter()


@router.get(
    "/results",
    response_model=list[CrawlResultResponse],
    summary="Get crawl results",
)
def get_results(
    crawl_run_id: int | None = Query(default=None, gt=0),
    source_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """Get crawl results with optional filters."""

    statement = select(CrawlResult)

    if crawl_run_id is not None:
        statement = statement.where(
            CrawlResult.crawl_run_id == crawl_run_id
        )

    if source_id is not None:
        statement = statement.join(
            CrawlRun,
            CrawlResult.crawl_run_id == CrawlRun.id,
        ).where(
            CrawlRun.source_id == source_id
        )

    statement = (
        statement
        .order_by(CrawlResult.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    return db.scalars(statement).all()


@router.get(
    "/results/{result_id}",
    response_model=CrawlResultResponse,
    summary="Get crawl result details",
)
def get_result(
    result_id: int,
    db: Session = Depends(get_db),
):
    """Get one crawl result including its HTML content."""

    result = db.get(CrawlResult, result_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Crawl result not found",
        )

    return result


@router.get(
    "/crawl-runs/{run_id}/results",
    response_model=list[CrawlResultResponse],
    summary="Get results of a crawl run",
)
def get_run_results(
    run_id: int,
    db: Session = Depends(get_db),
):
    """Get all results belonging to one crawl execution."""

    crawl_run = db.get(CrawlRun, run_id)

    if crawl_run is None:
        raise HTTPException(
            status_code=404,
            detail="Crawl run not found",
        )

    statement = (
        select(CrawlResult)
        .where(CrawlResult.crawl_run_id == run_id)
        .order_by(CrawlResult.created_at.desc())
    )

    return db.scalars(statement).all()
