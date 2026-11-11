
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models import Source
from backend.app.schemas.source import (
    SourceCreate,
    SourceUpdate,
    SourceResponse,
)


router = APIRouter()


@router.post(
    "/sources",
    response_model=SourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a data source",
)
def create_source(
    request: SourceCreate,
    db: Session = Depends(get_db),
):
    source = Source(
        name=request.name,
        base_url=str(request.base_url),
        description=request.description,
        is_active=request.is_active,
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


@router.get(
    "/sources",
    response_model=list[SourceResponse],
    summary="List all data sources",
)
def list_sources(
    db: Session = Depends(get_db),
):
    statement = select(Source).order_by(Source.id.desc())
    return db.scalars(statement).all()


@router.get(
    "/sources/{source_id}",
    response_model=SourceResponse,
    summary="Get a data source",
)
def get_source(
    source_id: int,
    db: Session = Depends(get_db),
):
    source = db.get(Source, source_id)

    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    return source


@router.patch(
    "/sources/{source_id}",
    response_model=SourceResponse,
    summary="Update a data source",
)
def update_source(
    source_id: int,
    request: SourceUpdate,
    db: Session = Depends(get_db),
):
    source = db.get(Source, source_id)

    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    update_data = request.model_dump(exclude_unset=True)

    for field in ("name", "base_url"):
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null",
            )

    if "base_url" in update_data:
        update_data["base_url"] = str(update_data["base_url"])

    for field, value in update_data.items():
        setattr(source, field, value)

    db.commit()
    db.refresh(source)

    return source


@router.delete(
    "/sources/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a data source",
)
def delete_source(
    source_id: int,
    db: Session = Depends(get_db),
):
    source = db.get(Source, source_id)

    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    db.delete(source)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
