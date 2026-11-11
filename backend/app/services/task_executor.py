
from sqlalchemy.orm import Session

from backend.app.core.fetch_engine import FetchEngine
from backend.app.models import Source, Task
from backend.app.schemas.fetch_result import FetchResult


class TaskExecutor:
    """
    Service responsible for manually executing crawling tasks.
    """

    def __init__(self):
        self.fetch_engine = FetchEngine()

    def execute(
        self,
        db: Session,
        task_id: int,
    ) -> FetchResult:
        """
        Execute one enabled task using its saved configuration.
        """

        task = db.get(Task, task_id)

        if task is None:
            raise LookupError("Task not found")

        if not task.is_enabled:
            raise ValueError("Task is disabled")

        source = db.get(Source, task.source_id)

        if source is None:
            raise LookupError("Data source not found")

        if not source.is_active:
            raise ValueError("Data source is disabled")

        config = task.schedule_config or {}

        url = config.get("url")

        if not isinstance(url, str) or not url.strip():
            raise ValueError(
                "Task configuration must contain a valid URL"
            )

        url = url.strip()

        if not url.startswith(("http://", "https://")):
            raise ValueError(
                "Only HTTP and HTTPS URLs are supported"
            )

        mode = config.get("mode", "fetcher")

        if mode not in ("fetcher", "browser"):
            raise ValueError(
                "Unsupported fetch mode. Use fetcher or browser"
            )

        wait_selector = config.get("wait_selector")

        if wait_selector is not None:
            if not isinstance(wait_selector, str):
                raise ValueError(
                    "wait_selector must be a string or null"
                )

            wait_selector = wait_selector.strip() or None

        return self.fetch_engine.fetch(
            db=db,
            source_id=source.id,
            url=url,
            mode=mode,
            wait_selector=wait_selector,
            task_id=task.id,
        )
