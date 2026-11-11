
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models import Source
from backend.app.core.fetch_engine import FetchEngine
from backend.app.schemas.fetch_request import FetchRequest
from backend.app.schemas.fetch_result import FetchResult


router = APIRouter()

fetch_engine = FetchEngine()


@router.post(
    "/fetch",
    response_model=FetchResult,
    summary="Fetch a webpage",
)
def fetch_webpage(
    request: FetchRequest,
    db: Session = Depends(get_db),
) -> FetchResult:
    """
    Fetch a webpage and persist its execution record and result.
    """

    source = db.get(Source, request.source_id)

    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    return fetch_engine.fetch(
        db=db,
        source_id=source.id,
        url=request.url,
        mode=request.mode,
        wait_selector=request.wait_selector,
    )
