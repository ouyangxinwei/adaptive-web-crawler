
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import Integer, func, select
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models import CrawlRun, Source, Task
from backend.app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)

from backend.app.services.task_executor import TaskExecutor
from backend.app.schemas.fetch_result import FetchResult


router = APIRouter()
task_executor = TaskExecutor()

def get_task_or_404(task_id: int, db: Session) -> Task:
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task

def get_task_statistics(task: Task, db: Session) -> dict:
    statistics = db.query(
        func.count(CrawlRun.id).label("total_runs"),
        func.sum(
            func.cast(CrawlRun.status == "success", Integer)
        ).label("success_runs"),
        func.sum(
            func.cast(CrawlRun.status == "failed", Integer)
        ).label("failed_runs"),
    ).filter(
        CrawlRun.task_id == task.id
    ).one()

    last_run = db.scalars(
        select(CrawlRun)
        .where(CrawlRun.task_id == task.id)
        .order_by(CrawlRun.started_at.desc(), CrawlRun.id.desc())
        .limit(1)
    ).first()

    return {
        "last_run_at": (
            last_run.finished_at or last_run.started_at
            if last_run else None
        ),
        "last_run_status": last_run.status if last_run else None,
        "total_runs": statistics.total_runs or 0,
        "success_runs": statistics.success_runs or 0,
        "failed_runs": statistics.failed_runs or 0,
    }


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a crawling task",
)
def create_task(
    request: TaskCreate,
    db: Session = Depends(get_db),
):
    source = db.get(Source, request.source_id)

    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found",
        )

    task = Task(
        source_id=request.source_id,
        name=request.name,
        schedule_type=request.schedule_type,
        schedule_config=request.schedule_config,
        is_enabled=request.is_enabled,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task



@router.get(
    "/tasks",
    response_model=list[TaskResponse],
    summary="List all crawling tasks",
)
def list_tasks(
    source_id: int | None = None,
    db: Session = Depends(get_db),
):
    statement = select(Task).order_by(Task.id.desc())

    if source_id is not None:
        statement = statement.where(Task.source_id == source_id)

    tasks = db.scalars(statement).all()

    return [
        {
            **TaskResponse.model_validate(task).model_dump(),
            **get_task_statistics(task, db),
        }
        for task in tasks
    ]


@router.get(
    "/sources/{source_id}/tasks",
    response_model=list[TaskResponse],
    summary="List tasks for a data source",
)

def list_source_tasks(
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
        select(Task)
        .where(Task.source_id == source_id)
        .order_by(Task.id.desc())
    )

    tasks = db.scalars(statement).all()

    return [
        {
            **TaskResponse.model_validate(task).model_dump(),
            **get_task_statistics(task, db),
        }
        for task in tasks
    ]

@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get a crawling task",
)


def get_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = get_task_or_404(task_id, db)

    return {
        **TaskResponse.model_validate(task).model_dump(),
        **get_task_statistics(task, db),
    }

@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update a crawling task",
)
def update_task(
    task_id: int,
    request: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = get_task_or_404(task_id, db)

    update_data: dict[str, Any] = request.model_dump(
        exclude_unset=True
    )

    for field in ("source_id", "name", "schedule_type", "schedule_config"):
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
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a crawling task",
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = get_task_or_404(task_id, db)

    db.delete(task)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/tasks/{task_id}/run",
    response_model=FetchResult,
    summary="Manually execute a crawling task",
)
def run_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    """Execute one crawling task manually."""

    try:
        return task_executor.execute(
            db=db,
            task_id=task_id,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
