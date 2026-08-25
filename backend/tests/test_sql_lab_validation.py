"""Unit tests for the SQL Lab's query validator — pure function, no DB
needed. The Postgres-role-level restrictions (verified manually with psql
during Phase 8: INSERT/DROP both fail with permission denied) are the real
security boundary; this is the defense-in-depth layer on top."""

import pytest

from app.services.sql_lab_service import QueryRejectedError, validate_query


def test_simple_select_is_allowed():
    assert validate_query("SELECT * FROM employees") == "SELECT * FROM employees"


def test_cte_with_statement_is_allowed():
    validate_query("WITH x AS (SELECT 1) SELECT * FROM x")


@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE employees",
        "INSERT INTO employees VALUES (1)",
        "UPDATE employees SET salary = 0",
        "DELETE FROM employees",
        "GRANT ALL ON employees TO PUBLIC",
        "TRUNCATE employees",
    ],
)
def test_write_statements_are_rejected(sql):
    with pytest.raises(QueryRejectedError):
        validate_query(sql)


def test_stacked_queries_are_rejected():
    with pytest.raises(QueryRejectedError):
        validate_query("SELECT 1; DROP TABLE employees;")


def test_comment_smuggled_second_statement_is_rejected():
    with pytest.raises(QueryRejectedError):
        validate_query("SELECT 1; -- comment\nINSERT INTO employees VALUES (99)")


def test_empty_query_is_rejected():
    with pytest.raises(QueryRejectedError):
        validate_query("   ")
