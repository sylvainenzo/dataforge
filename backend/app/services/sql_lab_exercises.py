"""A small, hand-written set of exercises against the seeded
sample_data.employees/departments schema — in-code rather than a database
table, since Phase 2's schema has no sql_exercises table and adding one for
three rows would be premature. If the SQL Lab grows real authoring volume,
this is the first thing to migrate into a proper table."""

from pydantic import BaseModel


class SqlExercise(BaseModel):
    id: str
    title: str
    prompt: str
    hint: str
    schema_description: str


EXERCISES: list[SqlExercise] = [
    SqlExercise(
        id="select-basics",
        title="Select the basics",
        prompt="List every employee's name and salary, highest salary first.",
        hint="ORDER BY salary DESC",
        schema_description="employees(id, name, department_id, salary, hire_date)",
    ),
    SqlExercise(
        id="filter-where",
        title="Filter with WHERE",
        prompt="Find every employee hired in 2022 or later.",
        hint="WHERE hire_date >= '2022-01-01'",
        schema_description="employees(id, name, department_id, salary, hire_date)",
    ),
    SqlExercise(
        id="join-departments",
        title="Your first JOIN",
        prompt="List each employee's name alongside their department name.",
        hint="JOIN departments ON employees.department_id = departments.id",
        schema_description="employees(id, name, department_id, salary, hire_date), departments(id, name, budget)",
    ),
    SqlExercise(
        id="aggregate-avg",
        title="Aggregate with GROUP BY",
        prompt="Find the average salary per department.",
        hint="GROUP BY department_id, use AVG(salary)",
        schema_description="employees(id, name, department_id, salary, hire_date)",
    ),
    SqlExercise(
        id="above-average",
        title="Above average",
        prompt="List every employee earning more than the company-wide average salary, highest first.",
        hint="WHERE salary > (SELECT AVG(salary) FROM employees)",
        schema_description="employees(id, name, department_id, salary, hire_date)",
    ),
]
