
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models import Rule, Source
from backend.app.schemas.rule import (
    RuleCreate,
    RuleUpdate,
    RuleResponse,
)


router = APIRouter()


def get_rule_or_404(rule_id: int, db: Session) -> Rule:
    rule = db.get(Rule, rule_id)

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found",
        )

    return rule


@router.post(
    "/rules",
    response_model=RuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an extraction rule",
)
def create_rule(
    request: RuleCreate,
    db: Session = Depends(get_db),
):
    source = db.get(Source, request.source_id)

    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    rule = Rule(
        source_id=request.source_id,
        name=request.name,
        selector=request.selector,
        selector_type=request.selector_type,
        field_name=request.field_name,
        extraction_config=request.extraction_config,
        is_active=request.is_active,
    )

    db.add(rule)
    db.commit()
    db.refresh(rule)

    return rule


@router.get(
    "/rules",
    response_model=list[RuleResponse],
    summary="List all extraction rules",
)
def list_rules(
    source_id: int | None = None,
    db: Session = Depends(get_db),
):
    statement = select(Rule).order_by(Rule.id.desc())

    if source_id is not None:
        statement = statement.where(Rule.source_id == source_id)

    return db.scalars(statement).all()


@router.get(
    "/rules/{rule_id}",
    response_model=RuleResponse,
    summary="Get an extraction rule",
)
def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
):
    return get_rule_or_404(rule_id, db)


@router.patch(
    "/rules/{rule_id}",
    response_model=RuleResponse,
    summary="Update an extraction rule",
)
def update_rule(
    rule_id: int,
    request: RuleUpdate,
    db: Session = Depends(get_db),
):
    rule = get_rule_or_404(rule_id, db)

    update_data: dict[str, Any] = request.model_dump(
        exclude_unset=True
    )

    required_fields = (
        "source_id",
        "name",
        "selector",
        "selector_type",
        "field_name",
        "extraction_config",
    )

    for field in required_fields:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null",
            )

    if "source_id" in update_data:
        source = db.get(Source, update_data["source_id"])

        if source is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Data source not found",
            )

    for field, value in update_data.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)

    return rule


@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an extraction rule",
)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
):
    rule = get_rule_or_404(rule_id, db)

    db.delete(rule)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/sources/{source_id}/rules",
    response_model=list[RuleResponse],
    summary="List rules for a data source",
)
def list_source_rules(
    source_id: int,
    db: Session = Depends(get_db),
):
    source = db.get(Source, source_id)

    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    statement = (
        select(Rule)
        .where(Rule.source_id == source_id)
        .order_by(Rule.id.desc())
    )

    return db.scalars(statement).all()
