"""Idempotent curriculum seed — real, original educational content (not
placeholder text). Two courses: "Python for Data Analysis" (5 lessons) and
"SQL Fundamentals" (3 lessons, conceptual companion to the interactive SQL
Lab's exercises). Content authoring at scale is ongoing work, not a
one-shot phase deliverable; this proves the data model end-to-end with
genuine material and keeps growing as more is written.

Run: python3 scripts/seed_curriculum.py
"""

import asyncio

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.assessment import QuestionType, Quiz, QuizQuestion
from app.models.base import LearningLevel
from app.models.curriculum import Course, LearningPath, LearningPathCourse, Lesson, LessonSkill, Module, Skill

VARIABLE_LESSON_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Explain what a variable is and why programs need them",
                "Create a variable in Python and read its value back",
                "Predict what happens when a variable is reassigned",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "A variable is a name you give to a piece of data so you can use it again later, "
                "the same way a label on a storage box tells you what's inside without opening it "
                "every time."
            ),
            "technical": (
                "In Python, a variable is a name bound to an object in memory. Assignment "
                "(`name = value`) does not copy data into a box; it points the name at an object. "
                "Reassigning a variable just points the name at a different object — it never "
                "mutates the original object unless the object itself is mutable and you call a "
                "method on it."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": "age = 29\nname = \"Priya\"\nis_student = False\n\nprint(name, \"is\", age, \"years old\")",
            "output": "Priya is 29 years old",
        },
        {
            "type": "exercise",
            "prompt": "Create a variable called `city` set to your favorite city, then print a sentence using it.",
            "starter_code": "city = ____\nprint(f\"I would love to visit {city}.\")",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Using a variable before it has been assigned a value (`NameError`).",
                "Confusing `=` (assignment) with `==` (equality comparison).",
                "Reusing a built-in name like `list` or `str` as a variable name, which shadows it.",
            ],
        },
        {
            "type": "summary",
            "text": "A variable names a value so your code can refer to it again. Assignment binds a name to an object; it doesn't create a copy.",
        },
        {
            "type": "key_terms",
            "items": ["variable", "assignment", "binding", "NameError"],
        },
    ]
}

DATAFRAME_LESSON_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Describe what a pandas DataFrame is and how it relates to a spreadsheet",
                "Load a small dataset into a DataFrame",
                "Select a single column and filter rows with a condition",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "A DataFrame is pandas' table object — rows and columns, like a spreadsheet, that "
                "you can filter, sort, and calculate on with code instead of clicking."
            ),
            "technical": (
                "A DataFrame is a 2-dimensional, size-mutable, labeled data structure with columns "
                "that can each hold a different dtype. It's built on top of NumPy arrays, and most "
                "pandas operations return a new DataFrame or Series rather than mutating in place "
                "unless you pass `inplace=True`."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "import pandas as pd\n\n"
                "data = {\"name\": [\"Amara\", \"Kofi\", \"Zanele\"], \"score\": [88, 72, 95]}\n"
                "df = pd.DataFrame(data)\n\n"
                "print(df[df[\"score\"] > 80])"
            ),
            "output": "     name  score\n0   Amara     88\n2  Zanele     95",
        },
        {
            "type": "exercise",
            "prompt": "Given the `df` above, select only the `name` column for rows where `score` is at least 90.",
            "starter_code": "result = df[df[\"score\"] ____][\"name\"]\nprint(result)",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Forgetting that `df[\"col\"]` returns a Series, not a DataFrame — `df[[\"col\"]]` keeps it as a DataFrame.",
                "Writing `df[\"score\" > 80]` instead of `df[df[\"score\"] > 80]` — the condition must reference the column, not a bare value.",
                "Assuming filtering mutates `df` — it returns a new object unless reassigned.",
            ],
        },
        {
            "type": "summary",
            "text": "A DataFrame is a labeled table backed by NumPy. Boolean indexing (`df[condition]`) is the standard way to filter rows.",
        },
        {
            "type": "key_terms",
            "items": ["DataFrame", "Series", "boolean indexing", "dtype"],
        },
    ]
}

LISTS_LOOPS_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Create a list and access items by position",
                "Loop over a list with a `for` loop",
                "Build up a new list from an existing one",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "A list holds many values in order, like a shopping list where each item has a "
                "position — the first item is position 0, not 1. A `for` loop lets you do the same "
                "thing to every item without writing it out by hand."
            ),
            "technical": (
                "Python lists are dynamic, ordered, mutable sequences that can hold mixed types, "
                "indexed from 0. `for item in my_list` iterates by calling `__iter__` under the "
                "hood; it does not require manual index tracking the way a C-style loop would."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "scores = [88, 72, 95, 61]\n\n"
                "for score in scores:\n"
                "    if score >= 70:\n"
                "        print(score, \"passed\")\n"
                "    else:\n"
                "        print(score, \"failed\")"
            ),
            "output": "88 passed\n72 passed\n95 passed\n61 failed",
        },
        {
            "type": "exercise",
            "prompt": "Build a new list `passing` containing only the scores from `scores` that are 70 or above, using a loop.",
            "starter_code": "scores = [88, 72, 95, 61]\npassing = []\nfor score in scores:\n    ____\nprint(passing)",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Off-by-one thinking: `scores[1]` is the *second* item, not the first — indexing starts at 0.",
                "Modifying a list while looping over it, which silently skips items.",
                "Using `scores[4]` on a 4-item list — the last valid index is 3, one less than the length.",
            ],
        },
        {
            "type": "summary",
            "text": "Lists hold ordered, zero-indexed values. `for item in list` is the standard way to process every item without manual counting.",
        },
        {
            "type": "key_terms",
            "items": ["list", "index", "for loop", "iteration"],
        },
    ]
}

CONDITIONALS_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Write an `if`/`elif`/`else` chain",
                "Combine conditions with `and`/`or`",
                "Explain why only one branch of an if/elif/else ever runs",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "Conditionals let your code make a decision — do this if something is true, "
                "otherwise do that. Python checks each condition in order and runs the first "
                "branch that matches, then skips the rest."
            ),
            "technical": (
                "`if`/`elif`/`else` is a single statement, not several independent ones — Python "
                "evaluates conditions top to bottom and executes exactly one branch (or none, if no "
                "condition matches and there's no `else`). Truthiness matters: `0`, `\"\"`, `None`, "
                "and empty containers are all falsy in a boolean context."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "temperature = 15\n\n"
                "if temperature > 25:\n"
                "    print(\"hot\")\n"
                "elif temperature > 10:\n"
                "    print(\"mild\")\n"
                "else:\n"
                "    print(\"cold\")"
            ),
            "output": "mild",
        },
        {
            "type": "exercise",
            "prompt": "Write a condition that prints \"weekday deal\" only when `day` is not \"Saturday\" and not \"Sunday\".",
            "starter_code": "day = \"Tuesday\"\nif ____:\n    print(\"weekday deal\")",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Writing `if x = 5` instead of `if x == 5` — `=` is assignment, not comparison, and Python will raise a SyntaxError here (unlike some languages that silently accept it).",
                "Chaining unrelated `if` statements instead of `elif` when the branches should be mutually exclusive — this can run more than one branch.",
                "Forgetting that `and`/`or` short-circuit — the second condition isn't even evaluated if the first already decides the result.",
            ],
        },
        {
            "type": "summary",
            "text": "if/elif/else picks exactly one branch by checking conditions in order. and/or combine conditions and short-circuit.",
        },
        {
            "type": "key_terms",
            "items": ["conditional", "elif", "truthiness", "short-circuit evaluation"],
        },
    ]
}

FUNCTIONS_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Define a function with parameters and a return value",
                "Explain the difference between printing and returning a value",
                "Call a function with keyword arguments",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "A function packages up a piece of logic so you can reuse it by name instead of "
                "retyping it. You give it inputs (parameters) and it can hand back an output "
                "(the return value)."
            ),
            "technical": (
                "`def` creates a function object bound to a name. `return` exits the function "
                "immediately with a value; a function with no `return` implicitly returns `None`. "
                "This is different from `print`, which only displays text and returns `None` — a "
                "common source of bugs is writing a function that prints a result instead of "
                "returning it, then trying to use that `None` later."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "def average(numbers):\n"
                "    return sum(numbers) / len(numbers)\n\n"
                "scores = [88, 72, 95, 61]\n"
                "print(average(scores))"
            ),
            "output": "79.0",
        },
        {
            "type": "exercise",
            "prompt": "Write a function `passed(score, threshold=70)` that returns True if score is at least threshold.",
            "starter_code": "def passed(score, threshold=70):\n    ____\n\nprint(passed(72))\nprint(passed(60))",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Using `print()` inside a function instead of `return`, then being surprised the caller gets `None`.",
                "Forgetting parentheses when calling a function — `average` refers to the function object itself, `average()` calls it.",
                "Giving a mutable default argument like `def f(items=[])` — the same list is reused across every call that doesn't pass one, which is rarely what you want.",
            ],
        },
        {
            "type": "summary",
            "text": "Functions package reusable logic. return hands back a value to the caller; print only displays text and returns None.",
        },
        {
            "type": "key_terms",
            "items": ["function", "parameter", "return value", "default argument"],
        },
    ]
}

SQL_SELECT_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Write a SELECT statement to retrieve specific columns",
                "Sort results with ORDER BY",
                "Limit how many rows come back",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "SQL is how you ask a database questions. SELECT says which columns you want, "
                "FROM says which table, and the database hands back matching rows — like asking "
                "a librarian for just the titles and authors instead of every book's full record."
            ),
            "technical": (
                "SQL is declarative: you describe the result set you want, not the steps to "
                "compute it — the query planner decides how. Column order in SELECT controls "
                "output order, not table order; ORDER BY is required if you need a guaranteed "
                "row order, since SQL tables are conceptually unordered sets."
            ),
        },
        {
            "type": "code",
            "language": "sql",
            "code": "SELECT name, salary\nFROM employees\nORDER BY salary DESC\nLIMIT 3;",
            "output": "     name      | salary\n----------------+--------\n Zanele Dlamini | 142000\n Amara Nwosu    | 128000\n Kofi Mensah    | 115000",
        },
        {
            "type": "exercise",
            "prompt": "Open the SQL Lab and try the \"Select the basics\" exercise — list every employee's name and salary, highest first.",
            "starter_code": "SELECT ____ FROM employees ORDER BY ____ DESC;",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Using `SELECT *` in real work when only specific columns are needed — it's fine for exploring, wasteful for production queries.",
                "Assuming row order is guaranteed without ORDER BY — a database is free to return rows in any order unless you ask for one.",
                "Forgetting that SQL keywords aren't case-sensitive but column/table names might be, depending on the database.",
            ],
        },
        {
            "type": "summary",
            "text": "SELECT ... FROM ... describes the result you want. ORDER BY controls row order; LIMIT caps how many rows come back.",
        },
        {
            "type": "key_terms",
            "items": ["SELECT", "FROM", "ORDER BY", "LIMIT"],
        },
    ]
}

SQL_WHERE_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Filter rows with WHERE",
                "Combine conditions with AND/OR",
                "Compare dates and check ranges",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "WHERE narrows down which rows come back — the same way filtering a spreadsheet "
                "hides rows that don't match, except the database never even sends the excluded "
                "rows to you."
            ),
            "technical": (
                "WHERE is evaluated per-row before any grouping or sorting happens — it filters "
                "the raw rows a table produces. This is why you can't reference an aggregate like "
                "COUNT(*) in a WHERE clause; that comes later in query execution (HAVING is for "
                "filtering after aggregation, a later topic)."
            ),
        },
        {
            "type": "code",
            "language": "sql",
            "code": "SELECT name, hire_date\nFROM employees\nWHERE hire_date >= '2022-01-01'\n  AND salary > 80000;",
            "output": "    name     | hire_date \n-------------+------------\n Kofi Mensah | 2022-07-01\n Priya Rao   | 2023-01-09",
        },
        {
            "type": "exercise",
            "prompt": "In the SQL Lab, try \"Filter with WHERE\" — find every employee hired in 2022 or later.",
            "starter_code": "SELECT * FROM employees WHERE hire_date ____;",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Using `=` to compare against NULL — NULL is never equal to anything, even itself; use `IS NULL` instead.",
                "Mixing AND/OR without parentheses when the logic isn't purely left-to-right, producing a filter that isn't what you intended.",
                "Quoting numbers unnecessarily (`WHERE salary = '80000'`) — usually harmless due to implicit conversion, but worth knowing which columns are actually text.",
            ],
        },
        {
            "type": "summary",
            "text": "WHERE filters rows before any grouping happens. Combine conditions with AND/OR, and use IS NULL to check for missing values.",
        },
        {
            "type": "key_terms",
            "items": ["WHERE", "AND", "OR", "IS NULL"],
        },
    ]
}

SQL_JOIN_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Explain why data is split across multiple tables",
                "Write an INNER JOIN to combine two tables",
                "Read a JOIN condition and predict which rows match",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "Real data is usually split across tables to avoid repeating information — an "
                "employees table doesn't repeat each department's full details on every row, it "
                "just stores a reference to it. JOIN stitches related tables back together for a "
                "query."
            ),
            "technical": (
                "An INNER JOIN returns only rows where the join condition matches in both tables "
                "— a department with no employees, or an employee with a NULL department_id, would "
                "be silently excluded. This is a normalized schema: departments.id is the primary "
                "key, employees.department_id is a foreign key referencing it."
            ),
        },
        {
            "type": "code",
            "language": "sql",
            "code": (
                "SELECT e.name, d.name AS department\n"
                "FROM employees e\n"
                "JOIN departments d ON e.department_id = d.id\n"
                "ORDER BY e.name\n"
                "LIMIT 3;"
            ),
            "output": "     name      | department  \n----------------+-------------\n Ahmed Farouk   | Sales\n Amara Nwosu    | Engineering\n Chloe Dubois   | Sales",
        },
        {
            "type": "exercise",
            "prompt": "In the SQL Lab, try \"Your first JOIN\" — list each employee's name alongside their department name.",
            "starter_code": "SELECT e.name, d.name\nFROM employees e\n____ departments d ON ____;",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Forgetting the ON condition, which produces a cross join — every row from one table paired with every row from the other, growing explosively.",
                "Joining on the wrong columns (e.g. name instead of id), which silently matches on the wrong basis if names aren't unique.",
                "Expecting an INNER JOIN to include unmatched rows — it won't; that's what LEFT JOIN is for, a later topic.",
            ],
        },
        {
            "type": "summary",
            "text": "JOIN combines rows from two tables based on a matching condition. INNER JOIN keeps only rows that match in both tables.",
        },
        {
            "type": "key_terms",
            "items": ["JOIN", "INNER JOIN", "foreign key", "primary key"],
        },
    ]
}

SQL_GROUPBY_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Use aggregate functions like COUNT, SUM, and AVG",
                "Group rows with GROUP BY to compute a value per category",
                "Filter grouped results with HAVING",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "Aggregate functions collapse many rows into one number — how many, how much, "
                "what's the average. GROUP BY does that separately for each category, the same "
                "way a pivot table gives you one subtotal row per group instead of one giant total."
            ),
            "technical": (
                "GROUP BY partitions the result set by the grouping column(s); every column in "
                "the SELECT list must then be either part of the GROUP BY or wrapped in an "
                "aggregate — the database can't return an ungrouped column when there could be "
                "multiple different values for it within a group. HAVING filters *after* "
                "aggregation, which is why it can reference an aggregate like COUNT(*) when WHERE "
                "cannot."
            ),
        },
        {
            "type": "code",
            "language": "sql",
            "code": (
                "SELECT department_id, COUNT(*) AS headcount, AVG(salary) AS avg_salary\n"
                "FROM employees\n"
                "GROUP BY department_id\n"
                "HAVING COUNT(*) > 2\n"
                "ORDER BY avg_salary DESC;"
            ),
            "output": " department_id | headcount | avg_salary \n---------------+-----------+------------\n             2 |         4 |   98500.00\n             1 |         3 |   87200.00",
        },
        {
            "type": "exercise",
            "prompt": "In the SQL Lab, try \"Aggregate with GROUP BY\" — find the average salary per department.",
            "starter_code": "SELECT department_id, ____(salary) AS avg_salary\nFROM employees\n____ BY department_id\nORDER BY avg_salary DESC;",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Selecting a raw column that isn't in GROUP BY and isn't aggregated — most databases reject this outright rather than picking an arbitrary value.",
                "Using WHERE to filter on an aggregate like COUNT(*) — WHERE runs before grouping, so it can't see the aggregate yet; use HAVING instead.",
                "Forgetting that COUNT(*) counts rows including NULLs, while COUNT(column) skips NULLs in that column — the two can give different answers.",
            ],
        },
        {
            "type": "summary",
            "text": "GROUP BY computes an aggregate per category. Every non-aggregated column in SELECT must appear in GROUP BY. HAVING filters after aggregation; WHERE filters before.",
        },
        {
            "type": "key_terms",
            "items": ["GROUP BY", "aggregate function", "HAVING", "COUNT"],
        },
    ]
}

SQL_SUBQUERY_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Write a subquery inside a WHERE clause",
                "Explain the difference between a subquery and a JOIN",
                "Recognize when a subquery is the clearer choice",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "A subquery is a query nested inside another query — you use the result of one "
                "question to answer a bigger one, like first finding \"today's average temperature\" "
                "and then asking \"which cities were above it.\""
            ),
            "technical": (
                "A subquery in a WHERE clause runs first (for an uncorrelated subquery, once "
                "total; for a correlated subquery, once per outer row) and its result feeds the "
                "outer query's condition. Anything a subquery can do here can usually be rewritten "
                "as a JOIN, and query planners often optimize them similarly — the choice is "
                "mostly about which is more readable for a given question."
            ),
        },
        {
            "type": "code",
            "language": "sql",
            "code": (
                "SELECT name, salary\n"
                "FROM employees\n"
                "WHERE salary > (SELECT AVG(salary) FROM employees)\n"
                "ORDER BY salary DESC;"
            ),
            "output": "     name       | salary \n----------------+--------\n Zanele Dlamini | 142000\n Amara Nwosu    | 128000",
        },
        {
            "type": "exercise",
            "prompt": "In the SQL Lab, try \"Above average\" — list every employee earning more than the company-wide average salary.",
            "starter_code": "SELECT name, salary\nFROM employees\nWHERE salary > (____);",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Writing a subquery that returns more than one row where the outer query expects exactly one (e.g. `= (SELECT ...)` on a multi-row result) — this raises an error at query time.",
                "Reaching for a subquery when a plain JOIN would be clearer, especially once you need columns from both tables in the final result — a WHERE subquery can only filter, it can't add columns.",
                "Forgetting a correlated subquery re-runs once per outer row, which can be slow on large tables if it isn't indexed well.",
            ],
        },
        {
            "type": "summary",
            "text": "A subquery nests one query inside another, most commonly to filter on a computed value like an average. Prefer a JOIN once you need columns from both tables.",
        },
        {
            "type": "key_terms",
            "items": ["subquery", "correlated subquery", "nested query"],
        },
    ]
}


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        # ---- Skills ----
        skill_names = {
            "python-fundamentals": "Python Fundamentals",
            "pandas-dataframes": "pandas DataFrames",
            "sql-fundamentals": "SQL Fundamentals",
        }
        skills: dict[str, Skill] = {}
        for slug, name in skill_names.items():
            existing = await db.execute(select(Skill).where(Skill.slug == slug))
            skill = existing.scalar_one_or_none()
            if skill is None:
                skill = Skill(name=name, slug=slug, category="python" if "sql" not in slug else "sql")
                db.add(skill)
                await db.flush()
            skills[slug] = skill

        # ---- Python for Data Analysis course ----
        existing_course = await db.execute(select(Course).where(Course.slug == "python-for-data-analysis"))
        py_course = existing_course.scalar_one_or_none()
        if py_course is None:
            py_course = Course(
                title="Python for Data Analysis",
                slug="python-for-data-analysis",
                description="Start from zero Python knowledge and build up to filtering real tabular data with pandas.",
                level=LearningLevel.BEGINNER,
                estimated_hours=6,
                published=True,
            )
            db.add(py_course)
            await db.flush()

        existing_module = await db.execute(
            select(Module).where(Module.course_id == py_course.id, Module.slug == "python-fundamentals")
        )
        py_module = existing_module.scalar_one_or_none()
        if py_module is None:
            py_module = Module(course_id=py_course.id, title="Python Fundamentals", slug="python-fundamentals", order=1)
            db.add(py_module)
            await db.flush()

        py_lesson_specs = [
            ("what-is-a-variable", "What Is a Variable?", 1, VARIABLE_LESSON_CONTENT, 10, "python-fundamentals"),
            ("lists-and-loops", "Lists and Loops", 2, LISTS_LOOPS_CONTENT, 15, "python-fundamentals"),
            ("conditionals", "Conditionals: if, elif, else", 3, CONDITIONALS_CONTENT, 12, "python-fundamentals"),
            ("functions", "Functions", 4, FUNCTIONS_CONTENT, 15, "python-fundamentals"),
            ("intro-to-pandas-dataframes", "Introduction to pandas DataFrames", 5, DATAFRAME_LESSON_CONTENT, 20, "pandas-dataframes"),
        ]
        lessons: dict[str, Lesson] = {}
        for slug, title, order, content, minutes, skill_slug in py_lesson_specs:
            existing_lesson = await db.execute(select(Lesson).where(Lesson.module_id == py_module.id, Lesson.slug == slug))
            lesson = existing_lesson.scalar_one_or_none()
            if lesson is None:
                lesson = Lesson(
                    module_id=py_module.id,
                    title=title,
                    slug=slug,
                    order=order,
                    content=content,
                    estimated_minutes=minutes,
                    published=True,
                )
                db.add(lesson)
                await db.flush()

                existing_link = await db.execute(
                    select(LessonSkill).where(LessonSkill.lesson_id == lesson.id, LessonSkill.skill_id == skills[skill_slug].id)
                )
                if existing_link.scalar_one_or_none() is None:
                    db.add(LessonSkill(lesson_id=lesson.id, skill_id=skills[skill_slug].id))
            else:
                # Keep ordering in sync even for a lesson row that already
                # existed from an earlier seed run (e.g. Phase 5's original
                # two lessons) — otherwise a newly inserted sibling can
                # collide with a stale `order` value.
                lesson.order = order
            lessons[slug] = lesson

        # ---- SQL Fundamentals course ----
        existing_sql_course = await db.execute(select(Course).where(Course.slug == "sql-fundamentals"))
        sql_course = existing_sql_course.scalar_one_or_none()
        if sql_course is None:
            sql_course = Course(
                title="SQL Fundamentals",
                slug="sql-fundamentals",
                description="The conceptual grounding behind the SQL Lab's exercises — SELECT, WHERE, JOIN, and aggregation.",
                level=LearningLevel.BEGINNER,
                estimated_hours=5,
                published=True,
            )
            db.add(sql_course)
            await db.flush()
        else:
            sql_course.description = "The conceptual grounding behind the SQL Lab's exercises — SELECT, WHERE, JOIN, and aggregation."
            sql_course.estimated_hours = 5

        existing_sql_module = await db.execute(
            select(Module).where(Module.course_id == sql_course.id, Module.slug == "sql-basics")
        )
        sql_module = existing_sql_module.scalar_one_or_none()
        if sql_module is None:
            sql_module = Module(course_id=sql_course.id, title="SQL Basics", slug="sql-basics", order=1)
            db.add(sql_module)
            await db.flush()

        sql_lesson_specs = [
            ("your-first-select", "Your First SELECT", 1, SQL_SELECT_CONTENT, 10, "sql-fundamentals"),
            ("filtering-with-where", "Filtering with WHERE", 2, SQL_WHERE_CONTENT, 10, "sql-fundamentals"),
            ("combining-tables-with-join", "Combining Tables with JOIN", 3, SQL_JOIN_CONTENT, 15, "sql-fundamentals"),
            ("aggregates-and-group-by", "Aggregates and GROUP BY", 4, SQL_GROUPBY_CONTENT, 15, "sql-fundamentals"),
            ("subqueries", "Subqueries", 5, SQL_SUBQUERY_CONTENT, 15, "sql-fundamentals"),
        ]
        for slug, title, order, content, minutes, skill_slug in sql_lesson_specs:
            existing_lesson = await db.execute(select(Lesson).where(Lesson.module_id == sql_module.id, Lesson.slug == slug))
            lesson = existing_lesson.scalar_one_or_none()
            if lesson is None:
                lesson = Lesson(
                    module_id=sql_module.id,
                    title=title,
                    slug=slug,
                    order=order,
                    content=content,
                    estimated_minutes=minutes,
                    published=True,
                )
                db.add(lesson)
                await db.flush()

                existing_link = await db.execute(
                    select(LessonSkill).where(LessonSkill.lesson_id == lesson.id, LessonSkill.skill_id == skills[skill_slug].id)
                )
                if existing_link.scalar_one_or_none() is None:
                    db.add(LessonSkill(lesson_id=lesson.id, skill_id=skills[skill_slug].id))
            else:
                lesson.order = order
            lessons[slug] = lesson

        # ---- Quiz on the variables lesson ----
        existing_quiz = await db.execute(select(Quiz).where(Quiz.lesson_id == lessons["what-is-a-variable"].id))
        quiz = existing_quiz.scalar_one_or_none()
        if quiz is None:
            quiz = Quiz(lesson_id=lessons["what-is-a-variable"].id, title="Variables Check", passing_score=70)
            db.add(quiz)
            await db.flush()

            db.add_all(
                [
                    QuizQuestion(
                        quiz_id=quiz.id,
                        question_text="What does `age = 29` do in Python?",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options={
                            "choices": [
                                "Binds the name age to the integer object 29",
                                "Compares age to 29",
                                "Creates a new file called age",
                                "Deletes the variable age",
                            ]
                        },
                        correct_answer={"value": "Binds the name age to the integer object 29"},
                        explanation="`=` is assignment: it binds a name to an object, it does not compare or delete anything.",
                        order=1,
                        points=1,
                    ),
                    QuizQuestion(
                        quiz_id=quiz.id,
                        question_text="Which operator checks equality instead of assigning a value?",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options={"choices": ["=", "==", ":=", "!="]},
                        correct_answer={"value": "=="},
                        explanation="`==` compares two values; `=` assigns.",
                        order=2,
                        points=1,
                    ),
                ]
            )

        # ---- Quiz on the functions lesson ----
        existing_fn_quiz = await db.execute(select(Quiz).where(Quiz.lesson_id == lessons["functions"].id))
        fn_quiz = existing_fn_quiz.scalar_one_or_none()
        if fn_quiz is None:
            fn_quiz = Quiz(lesson_id=lessons["functions"].id, title="Functions Check", passing_score=70)
            db.add(fn_quiz)
            await db.flush()

            db.add_all(
                [
                    QuizQuestion(
                        quiz_id=fn_quiz.id,
                        question_text="What does a function return if it has no `return` statement?",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options={"choices": ["None", "0", "An empty string", "An error, always"]},
                        correct_answer={"value": "None"},
                        explanation="A function without an explicit return implicitly returns None.",
                        order=1,
                        points=1,
                    ),
                    QuizQuestion(
                        quiz_id=fn_quiz.id,
                        question_text="print(x) and return x do the same thing.",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options={"choices": ["True", "False"]},
                        correct_answer={"value": "False"},
                        explanation="print only displays text and returns None; return hands the value back to the caller so it can be used.",
                        order=2,
                        points=1,
                    ),
                ]
            )

        # ---- Quiz on the GROUP BY lesson ----
        existing_gb_quiz = await db.execute(select(Quiz).where(Quiz.lesson_id == lessons["aggregates-and-group-by"].id))
        gb_quiz = existing_gb_quiz.scalar_one_or_none()
        if gb_quiz is None:
            gb_quiz = Quiz(lesson_id=lessons["aggregates-and-group-by"].id, title="GROUP BY Check", passing_score=70)
            db.add(gb_quiz)
            await db.flush()

            db.add_all(
                [
                    QuizQuestion(
                        quiz_id=gb_quiz.id,
                        question_text="Which clause filters rows AFTER aggregation, so it can reference COUNT(*)?",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options={"choices": ["WHERE", "HAVING", "GROUP BY", "ORDER BY"]},
                        correct_answer={"value": "HAVING"},
                        explanation="WHERE filters before grouping happens; HAVING filters the grouped/aggregated results.",
                        order=1,
                        points=1,
                    ),
                    QuizQuestion(
                        quiz_id=gb_quiz.id,
                        question_text="COUNT(*) and COUNT(some_column) always return the same number.",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options={"choices": ["True", "False"]},
                        correct_answer={"value": "False"},
                        explanation="COUNT(*) counts every row; COUNT(column) skips rows where that column is NULL, so they can differ.",
                        order=2,
                        points=1,
                    ),
                ]
            )

        # ---- Learning path wrapping both courses ----
        existing_path = await db.execute(select(LearningPath).where(LearningPath.slug == "data-analytics-foundations"))
        path = existing_path.scalar_one_or_none()
        if path is None:
            path = LearningPath(
                title="Data Analytics Foundations",
                slug="data-analytics-foundations",
                description="The on-ramp for Data Analytics: no prior programming experience assumed.",
                published=True,
            )
            db.add(path)
            await db.flush()

        for course, order in [(py_course, 1), (sql_course, 2)]:
            existing_lpc = await db.execute(
                select(LearningPathCourse).where(
                    LearningPathCourse.learning_path_id == path.id, LearningPathCourse.course_id == course.id
                )
            )
            if existing_lpc.scalar_one_or_none() is None:
                db.add(LearningPathCourse(learning_path_id=path.id, course_id=course.id, order=order))

        await db.commit()
        print(
            f"Seed complete: {len(skill_names)} skills, 2 courses "
            f"({len(py_lesson_specs)} + {len(sql_lesson_specs)} lessons), 3 quizzes, 1 learning path."
        )


if __name__ == "__main__":
    asyncio.run(seed())
