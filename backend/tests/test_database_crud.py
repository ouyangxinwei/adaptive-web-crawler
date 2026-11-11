
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from backend.app.database.session import engine
from backend.app.models import (
    CrawlResult,
    CrawlRun,
    Rule,
    Source,
    SystemSetting,
    Task,
)
from uuid import uuid4

test_key = f"crud_test_{uuid4().hex}"

def test_database_crud():
    """
    Test PostgreSQL CRUD operations using a rollback-only transaction.
    All inserted test data will be rolled back.
    """

    connection = engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )

    try:
        # 1. Create Source
        source = Source(
            name="CRUD Test Source",
            base_url="https://example.com",
            description="Temporary database CRUD test",
        )
        session.add(source)
        session.flush()

        assert source.id is not None
        assert source.is_active is True

        # 2. Create Task
        task = Task(
            source_id=source.id,
            name="CRUD Test Task",
            schedule_type="manual",
            schedule_config={"type": "manual"},
        )
        session.add(task)

        # 3. Create Rule
        rule = Rule(
            source_id=source.id,
            name="CRUD Test Rule",
            selector="h1",
            selector_type="css",
            field_name="title",
            extraction_config={"attribute": "text"},
        )
        session.add(rule)

        # 4. Create CrawlRun
        crawl_run = CrawlRun(
            source_id=source.id,
            task=task,
            status="success",
            fetch_mode="fetcher",
            items_count=1,
        )
        session.add(crawl_run)
        session.flush()

        # 5. Create CrawlResult
        result = CrawlResult(
            crawl_run_id=crawl_run.id,
            url="https://example.com",
            title="CRUD Test Result",
            data={"title": "CRUD Test Result"},
            content="Temporary test content",
        )
        session.add(result)

        # 6. Create SystemSetting
        setting = SystemSetting(
            key="test_key",
            value={"enabled": True},
            description="Temporary CRUD test setting",
        )
        session.add(setting)

        session.commit()

        # 7. Read and verify relationships
        loaded_source = session.scalar(
            select(Source).where(Source.id == source.id)
        )

        assert loaded_source is not None
        assert len(loaded_source.tasks) == 1
        assert len(loaded_source.rules) == 1
        assert len(loaded_source.crawl_runs) == 1

        loaded_run = session.scalar(
            select(CrawlRun).where(CrawlRun.id == crawl_run.id)
        )

        assert loaded_run is not None
        assert len(loaded_run.results) == 1

        loaded_setting = session.scalar(
            select(SystemSetting).where(
                SystemSetting.key == "test_key"
            )
        )

        assert loaded_setting is not None
        assert loaded_setting.value == {"enabled": True}

        # 8. Update
        loaded_source.name = "CRUD Test Source Updated"
        loaded_setting.value = {"enabled": False}
        session.commit()

        session.refresh(loaded_source)
        session.refresh(loaded_setting)

        assert loaded_source.name == "CRUD Test Source Updated"
        assert loaded_setting.value == {"enabled": False}

        # 9. Delete one result and verify
        session.delete(loaded_run.results[0])
        session.flush()

        remaining_result = session.scalar(
            select(CrawlResult).where(
                CrawlResult.crawl_run_id == loaded_run.id
            )
        )

        assert remaining_result is None

        # 10. Verify database tables are present
        inspector = inspect(connection)
        table_names = set(inspector.get_table_names())

        expected_tables = {
            "sources",
            "tasks",
            "rules",
            "crawl_runs",
            "crawl_results",
            "system_settings",
        }

        assert expected_tables.issubset(table_names)

    finally:
        session.close()

        # Roll back all test data, including committed savepoints.
        transaction.rollback()
        connection.close()
