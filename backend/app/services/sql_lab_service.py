import re

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

MAX_ROWS = 500

# Defense in depth — the sql_lab_readonly Postgres role already cannot
# execute any of these (verified directly with psql: INSERT and DROP both
# return "permission denied"/"must be owner"), but rejecting them before
# they reach the database gives a clearer error message than a raw
# Postgres permission error, and costs nothing.
_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|GRANT|REVOKE|TRUNCATE|COPY|EXECUTE|CALL|VACUUM|ATTACH)\b",
    re.IGNORECASE,
)
_COMMENT_STRIP = re.compile(r"--[^\n]*|/\*.*?\*/", re.DOTALL)


class QueryRejectedError(Exception):
    pass


def validate_query(sql: str) -> str:
    stripped = sql.strip()
    if not stripped:
        raise QueryRejectedError("Query is empty.")

    without_comments = _COMMENT_STRIP.sub(" ", stripped).strip()

    # Allow exactly one optional trailing semicolon, reject anything that
    # looks like multiple statements.
    body = without_comments[:-1] if without_comments.endswith(";") else without_comments
    if ";" in body:
        raise QueryRejectedError("Only a single statement is allowed per run.")

    if not re.match(r"^\s*(SELECT|WITH)\b", body, re.IGNORECASE):
        raise QueryRejectedError("Only SELECT statements are allowed in the SQL Lab.")

    if _FORBIDDEN_KEYWORDS.search(body):
        raise QueryRejectedError("That keyword isn't allowed in the SQL Lab — this is a read-only sandbox.")

    return body


async def run_query(db: AsyncSession, sql: str) -> tuple[list[str], list[list], bool]:
    validated = validate_query(sql)
    try:
        result = await db.execute(text(validated))
    except DBAPIError as exc:
        # Surface Postgres's own error message (e.g. "column x does not
        # exist") — that's the actual teaching moment for a SQL exercise.
        raise QueryRejectedError(str(exc.orig)) from exc

    columns = list(result.keys())
    rows = result.fetchmany(MAX_ROWS + 1)
    truncated = len(rows) > MAX_ROWS
    return columns, [list(row) for row in rows[:MAX_ROWS]], truncated
