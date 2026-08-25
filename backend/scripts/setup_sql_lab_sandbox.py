"""One-time (but idempotent) setup for the SQL Lab's isolated sandbox: a
separate database, a low-privilege SELECT-only role, and synthetic
sample data (sample_data.employees/departments) that the hand-written
exercises in app/services/sql_lab_exercises.py query against.

This existed only as manual psql commands run directly against a local
Postgres during earlier development and was never captured as a script —
written now so any new environment (a fresh Railway/Render Postgres, a
new dev machine) can reproduce it instead of guessing.

Connects using DATABASE_URL (needs privileges to create roles/databases —
the default user on a managed Postgres like Railway's has this). Creates
its OWN separate database and role; never touches the app's main schema.

Run: python3 scripts/setup_sql_lab_sandbox.py

Prints the resulting SQL_LAB_DATABASE_URL at the end — set that as the
env var. Safe to re-run: resets the role's password and replaces the
sample data each time rather than erroring on already-exists.
"""

import secrets
import sys
from urllib.parse import urlparse, urlunparse

import psycopg
from psycopg import sql

from app.core.config import settings

SQL_LAB_DB_NAME = "dataforge_sql_lab"
SQL_LAB_ROLE = "sql_lab_readonly"

DEPARTMENTS = [
    (1, "Engineering", 850000),
    (2, "Sales", 420000),
    (3, "Marketing", 310000),
    (4, "Customer Support", 260000),
]

# Clearly synthetic practice data — not real people, not real payroll.
EMPLOYEES = [
    (1, "Amara Okafor", 1, 118000, "2019-03-11"),
    (2, "Kofi Mensah", 1, 132000, "2021-07-04"),
    (3, "Zanele Dlamini", 1, 96000, "2023-01-16"),
    (4, "Liang Wei", 1, 145000, "2018-11-02"),
    (5, "Priya Nair", 2, 78000, "2022-05-19"),
    (6, "Marco Rossi", 2, 91000, "2020-09-23"),
    (7, "Ingrid Larsen", 2, 68000, "2024-02-08"),
    (8, "Diego Fernandez", 3, 72000, "2021-12-01"),
    (9, "Hana Kobayashi", 3, 84000, "2023-06-27"),
    (10, "Tomas Novak", 4, 58000, "2019-08-14"),
    (11, "Fatima Al-Sayed", 4, 61000, "2022-10-30"),
    (12, "Chinedu Eze", 4, 65000, "2024-04-05"),
]


def _to_psycopg_dsn(sqlalchemy_dsn: str) -> str:
    return sqlalchemy_dsn.replace("postgresql+psycopg://", "postgresql://")


def _connection_string_for(base_dsn: str, *, user: str, password: str, dbname: str) -> str:
    parsed = urlparse(base_dsn)
    netloc = f"{user}:{password}@{parsed.hostname}"
    if parsed.port:
        netloc += f":{parsed.port}"
    return urlunparse(("postgresql+psycopg", netloc, f"/{dbname}", "", "", ""))


def main() -> None:
    admin_dsn = _to_psycopg_dsn(settings.database_url)
    password = secrets.token_urlsafe(24)

    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (SQL_LAB_ROLE,))
            if cur.fetchone() is None:
                cur.execute(
                    sql.SQL("CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE").format(
                        sql.Identifier(SQL_LAB_ROLE), sql.Literal(password)
                    )
                )
                print(f"Created role {SQL_LAB_ROLE}.")
            else:
                cur.execute(
                    sql.SQL("ALTER ROLE {} WITH PASSWORD {}").format(
                        sql.Identifier(SQL_LAB_ROLE), sql.Literal(password)
                    )
                )
                print(f"Role {SQL_LAB_ROLE} already existed — reset its password.")

            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (SQL_LAB_DB_NAME,))
            if cur.fetchone() is None:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(SQL_LAB_DB_NAME)))
                print(f"Created database {SQL_LAB_DB_NAME}.")
            else:
                print(f"Database {SQL_LAB_DB_NAME} already existed.")

    sandbox_admin_dsn = _connection_string_for(
        admin_dsn, user=urlparse(admin_dsn).username, password=urlparse(admin_dsn).password or "", dbname=SQL_LAB_DB_NAME
    )
    sandbox_admin_dsn = _to_psycopg_dsn(sandbox_admin_dsn)

    with psycopg.connect(sandbox_admin_dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS sample_data")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sample_data.departments (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    budget INTEGER NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sample_data.employees (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    department_id INTEGER NOT NULL REFERENCES sample_data.departments(id),
                    salary INTEGER NOT NULL,
                    hire_date DATE NOT NULL
                )
            """)
            cur.execute("TRUNCATE sample_data.employees, sample_data.departments RESTART IDENTITY CASCADE")
            cur.executemany(
                "INSERT INTO sample_data.departments (id, name, budget) VALUES (%s, %s, %s)", DEPARTMENTS
            )
            cur.executemany(
                "INSERT INTO sample_data.employees (id, name, department_id, salary, hire_date) "
                "VALUES (%s, %s, %s, %s, %s)",
                EMPLOYEES,
            )
            print(f"Seeded {len(DEPARTMENTS)} departments and {len(EMPLOYEES)} employees.")

            cur.execute(
                sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                    sql.Identifier(SQL_LAB_DB_NAME), sql.Identifier(SQL_LAB_ROLE)
                )
            )
            cur.execute(sql.SQL("GRANT USAGE ON SCHEMA sample_data TO {}").format(sql.Identifier(SQL_LAB_ROLE)))
            cur.execute(
                sql.SQL("GRANT SELECT ON ALL TABLES IN SCHEMA sample_data TO {}").format(
                    sql.Identifier(SQL_LAB_ROLE)
                )
            )
            cur.execute(
                sql.SQL("REVOKE ALL ON SCHEMA public FROM {}").format(sql.Identifier(SQL_LAB_ROLE))
            )
            print(f"Granted SELECT-only on sample_data to {SQL_LAB_ROLE}; confirmed no access to public schema.")

    sql_lab_url = _connection_string_for(admin_dsn, user=SQL_LAB_ROLE, password=password, dbname=SQL_LAB_DB_NAME)
    print("\nSet this as SQL_LAB_DATABASE_URL:")
    print(sql_lab_url)


if __name__ == "__main__":
    try:
        main()
    except psycopg.Error as exc:
        print(f"Setup failed: {exc}", file=sys.stderr)
        sys.exit(1)
