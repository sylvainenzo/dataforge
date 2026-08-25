from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

# A separate engine, connected as the low-privilege sql_lab_readonly role
# (SELECT-only, restricted to the sample_data schema — verified directly
# with psql during Phase 8 development: INSERT and DROP both fail with
# permission denied). Deliberately never shares a connection pool with the
# app's own database.
sql_lab_engine = create_async_engine(settings.sql_lab_database_url, future=True)
SqlLabSessionLocal = async_sessionmaker(bind=sql_lab_engine, autoflush=False, expire_on_commit=False)
