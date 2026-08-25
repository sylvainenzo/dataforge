"""Idempotent curriculum seed — the "practical" (intermediate) tier above
the beginner Python/SQL/Statistics courses: "Intermediate Python",
"Intermediate SQL", and "Intermediate Statistics" (3 lessons each), added
to the existing "Data Analytics Foundations" learning path. This is part
of expanding the curriculum from a single beginner tier toward the full
beginner-to-expert range the platform is meant to cover.

Run: python3 scripts/seed_curriculum_intermediate.py
(Run seed_curriculum.py and seed_curriculum_stats_wrangling.py first —
this reuses their learning path and skills.)
"""

import asyncio

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.assessment import QuestionType, Quiz, QuizQuestion
from app.models.base import LearningLevel
from app.models.curriculum import Course, LearningPath, LearningPathCourse, Lesson, LessonSkill, Module, Skill

LIST_COMPREHENSIONS_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Rewrite a simple for-loop that builds a list as a list comprehension",
                "Add a filtering condition to a comprehension",
                "Recognize when a comprehension has become too complex to be readable",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "A list comprehension is a compact way to build a new list from an existing one in a single "
                "line — write down what each new item should be, and optionally which items to keep, all in "
                "one expression instead of a multi-line loop."
            ),
            "technical": (
                "`[expr for item in iterable if condition]` desugars to essentially the same bytecode as an "
                "explicit loop appending to a list, but runs slightly faster in CPython since it avoids "
                "repeated attribute lookups for `.append`. Readability, not performance, is the usual reason "
                "to reach for one — past two clauses (one `for`, one `if`), a regular loop is usually clearer."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "scores = [88, 72, 95, 61, 79]\n\n"
                "# Explicit loop\n"
                "passing = []\n"
                "for score in scores:\n"
                "    if score >= 70:\n"
                "        passing.append(score)\n\n"
                "# Same result, as a comprehension\n"
                "passing = [score for score in scores if score >= 70]\n"
                "print(passing)"
            ),
            "output": "[88, 72, 95, 79]",
        },
        {
            "type": "exercise",
            "prompt": "Write a comprehension that squares every number in `nums` that is even.",
            "starter_code": "nums = [1, 2, 3, 4, 5, 6]\nresult = [____ for n in nums if ____]\nprint(result)",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Nesting two or three `for`/`if` clauses in one comprehension until it's harder to read than the loop it replaced — that's a sign to go back to a regular loop.",
                "Using a comprehension purely for a side effect (like printing) instead of building a list — a plain `for` loop is clearer when you don't need the resulting list.",
                "Forgetting the expression comes first: `[item for item in x]`, not `[for item in x: item]` — comprehension syntax doesn't use a colon.",
            ],
        },
        {
            "type": "summary",
            "text": "A list comprehension builds a new list in one expression: [expr for item in iterable if condition]. Prefer it for simple transforms and filters; prefer a loop once it gets complex.",
        },
        {
            "type": "key_terms",
            "items": ["list comprehension", "iterable", "filter clause"],
        },
    ]
}

FILES_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Read and write a text file using a context manager",
                "Read a CSV file into a list of rows without pandas",
                "Explain why files should be opened with `with` instead of manually calling close()",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "Programs often need to read data from a file on disk, or save results to one. Python's `open()` "
                "gives you a handle to a file, and `with` makes sure it gets closed automatically, even if "
                "something goes wrong while reading it."
            ),
            "technical": (
                "`with open(path) as f:` is a context manager — it calls `f.close()` in a `finally` block "
                "behind the scenes, guaranteeing the file handle is released even if an exception is raised "
                "inside the block. Manually calling `.close()` after read/write code doesn't give you that "
                "guarantee unless it's wrapped in its own try/finally."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "import csv\n\n"
                "with open(\"scores.csv\", newline=\"\") as f:\n"
                "    reader = csv.DictReader(f)\n"
                "    rows = list(reader)\n\n"
                "print(rows[0])"
            ),
            "output": "{'name': 'Amara', 'score': '88'}",
        },
        {
            "type": "exercise",
            "prompt": "Every value from csv.DictReader comes back as a string, even the score column. Write a line that converts row['score'] to an int.",
            "starter_code": "row = {\"name\": \"Amara\", \"score\": \"88\"}\nrow[\"score\"] = ____\nprint(row)",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Forgetting that every field from csv.DictReader is a string — `row['score'] > 80` compares a string to an int and raises a TypeError, not a helpful number comparison.",
                "Opening a file without `with` and forgetting to close it, which can leak file handles in a long-running program.",
                "Forgetting `newline=\"\"` when opening a CSV on some platforms — the csv module handles line endings itself and can double up blank lines otherwise.",
            ],
        },
        {
            "type": "summary",
            "text": "with open(path) as f manages closing the file automatically. csv.DictReader turns CSV rows into dicts, but every value is a string until you convert it.",
        },
        {
            "type": "key_terms",
            "items": ["context manager", "file handle", "csv.DictReader"],
        },
    ]
}

ERROR_HANDLING_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Catch a specific exception with try/except",
                "Explain why catching a bare `except:` is usually a mistake",
                "Use `finally` for cleanup that must always run",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "Things go wrong — a file might not exist, a conversion might fail. `try`/`except` lets your "
                "program catch that failure and respond instead of crashing outright."
            ),
            "technical": (
                "Python's exceptions form a class hierarchy (`ValueError`, `KeyError`, and so on all inherit "
                "from `Exception`). Catching a specific exception type documents exactly what you expect to go "
                "wrong; a bare `except:` also silently catches things you didn't anticipate — including typos "
                "that raise `NameError` — making bugs much harder to find."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "def safe_divide(a, b):\n"
                "    try:\n"
                "        return a / b\n"
                "    except ZeroDivisionError:\n"
                "        return None\n\n"
                "print(safe_divide(10, 2))\n"
                "print(safe_divide(10, 0))"
            ),
            "output": "5.0\nNone",
        },
        {
            "type": "exercise",
            "prompt": "Write a function that converts a string to an int, returning None if the string isn't a valid number, instead of letting the ValueError crash the program.",
            "starter_code": "def safe_int(text):\n    try:\n        return int(text)\n    except ____:\n        return None\n\nprint(safe_int(\"42\"))\nprint(safe_int(\"abc\"))",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Using a bare `except:` (or `except Exception:` without a real reason), which can hide real bugs alongside the error you meant to catch.",
                "Catching an exception and silently doing nothing (`except Exception: pass`) — this makes failures invisible instead of handled.",
                "Putting too much code inside the `try` block, so it's unclear which line could actually raise the exception being caught.",
            ],
        },
        {
            "type": "summary",
            "text": "try/except catches specific, expected failures. Catch the narrowest exception type that applies, and avoid bare except clauses that can hide real bugs.",
        },
        {
            "type": "key_terms",
            "items": ["exception", "try/except", "ValueError", "finally"],
        },
    ]
}

WINDOW_FUNCTIONS_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Explain how a window function differs from GROUP BY",
                "Use ROW_NUMBER() to rank rows within a partition",
                "Use PARTITION BY to compute a value per group without collapsing rows",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "GROUP BY collapses many rows into one summary row per group. A window function computes a "
                "value across a group of related rows too, but keeps every original row — useful for things "
                "like \"rank each employee's salary within their department\" where you still want one row per "
                "employee."
            ),
            "technical": (
                "`ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC)` computes a per-partition ranking "
                "without reducing the row count, unlike an aggregate + GROUP BY. `PARTITION BY` defines the "
                "window (the set of rows the function sees); `ORDER BY` inside the same `OVER()` clause "
                "controls ranking order within that window."
            ),
        },
        {
            "type": "code",
            "language": "sql",
            "code": (
                "SELECT name, department_id, salary,\n"
                "       ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_rank\n"
                "FROM employees\n"
                "ORDER BY department_id, dept_rank;"
            ),
            "output": "     name     | department_id | salary | dept_rank \n----------------+---------------+--------+-----------\n Zanele Dlamini |             1 | 142000 |         1\n Kofi Mensah    |             1 |  98000 |         2\n Amara Nwosu    |             2 | 128000 |         1",
        },
        {
            "type": "exercise",
            "prompt": "In the SQL Lab, rank employees by salary within their own department, highest first.",
            "starter_code": "SELECT name, department_id, salary,\n       ____() OVER (PARTITION BY department_id ORDER BY salary DESC)\nFROM employees;",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Forgetting PARTITION BY and getting one ranking across the whole table instead of per group.",
                "Confusing ROW_NUMBER() (always unique, 1/2/3...) with RANK() (ties share a rank, and the next rank skips) — they give different results whenever there's a tie.",
                "Trying to filter on a window function directly in WHERE — window functions run after WHERE, so you need a subquery or CTE to filter on their result.",
            ],
        },
        {
            "type": "summary",
            "text": "Window functions compute per-group values without collapsing rows, unlike GROUP BY. PARTITION BY defines the window; ORDER BY inside OVER() controls ranking.",
        },
        {
            "type": "key_terms",
            "items": ["window function", "ROW_NUMBER", "PARTITION BY", "OVER"],
        },
    ]
}

CTE_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Write a query using WITH to define a common table expression",
                "Explain why a CTE can make a complex query more readable than nested subqueries",
                "Reference a CTE more than once in the same query",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "A CTE is a named, temporary result set you define at the top of a query with `WITH`, then use "
                "like a table in the rest of the query — a way to break a complicated query into readable "
                "named steps instead of nesting nested subqueries inside each other."
            ),
            "technical": (
                "`WITH name AS (SELECT ...) SELECT ... FROM name` — the CTE is materialized or inlined "
                "depending on the query planner, but semantically it behaves like a temporary view scoped to "
                "that one query. Unlike a subquery, a CTE can be referenced multiple times in the outer query "
                "without repeating its definition, and multiple CTEs can be chained, each able to reference "
                "the ones defined before it."
            ),
        },
        {
            "type": "code",
            "language": "sql",
            "code": (
                "WITH department_averages AS (\n"
                "    SELECT department_id, AVG(salary) AS avg_salary\n"
                "    FROM employees\n"
                "    GROUP BY department_id\n"
                ")\n"
                "SELECT e.name, e.salary, d.avg_salary\n"
                "FROM employees e\n"
                "JOIN department_averages d ON d.department_id = e.department_id\n"
                "WHERE e.salary > d.avg_salary;"
            ),
            "output": "     name       | salary | avg_salary \n----------------+--------+------------\n Zanele Dlamini | 142000 |   98500.00",
        },
        {
            "type": "exercise",
            "prompt": "In the SQL Lab, use a CTE to find every employee earning above their own department's average salary.",
            "starter_code": "WITH dept_avg AS (\n    SELECT department_id, AVG(salary) AS avg_salary\n    FROM employees\n    GROUP BY department_id\n)\nSELECT ____\nFROM employees e JOIN dept_avg d ON ____\nWHERE ____;",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Reaching for a CTE when a single simple query would do — they're a readability tool for genuinely multi-step logic, not a default for every query.",
                "Assuming a CTE is always faster than a subquery — depending on the database, it may or may not be materialized, so it's not automatically a performance optimization.",
                "Forgetting a later CTE can reference an earlier one, but not the other way around — they're defined and resolved in order.",
            ],
        },
        {
            "type": "summary",
            "text": "WITH defines a named, temporary result set (a CTE) that the rest of the query can reference like a table, making complex logic easier to read than nested subqueries.",
        },
        {
            "type": "key_terms",
            "items": ["CTE", "WITH clause", "common table expression"],
        },
    ]
}

NULL_HANDLING_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Explain why NULL = NULL is never true in SQL",
                "Use COALESCE to substitute a default value for NULL",
                "Predict how NULL affects aggregate functions and arithmetic",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "NULL means \"unknown\" or \"missing,\" not zero or an empty string. Because it represents "
                "an unknown value, SQL won't even say a NULL is equal to another NULL — comparing two unknowns "
                "can't honestly be answered yes or no, so both `=` and `!=` involving NULL return NULL, not "
                "true or false."
            ),
            "technical": (
                "`COALESCE(a, b, c, ...)` returns the first non-NULL argument, and is the standard way to "
                "supply a default. Any arithmetic expression involving a NULL operand evaluates to NULL "
                "(`5 + NULL` is NULL, not 5), and most aggregate functions (`SUM`, `AVG`, `COUNT(column)`) "
                "simply skip NULL rows rather than treating them as zero — which is why `AVG` over a column "
                "with NULLs computes the average of the non-NULL values only, not counting NULLs as zero."
            ),
        },
        {
            "type": "code",
            "language": "sql",
            "code": (
                "SELECT name, COALESCE(bonus, 0) AS bonus\n"
                "FROM employees\n"
                "ORDER BY name;"
            ),
            "output": "     name       | bonus \n----------------+-------\n Amara Nwosu    |  5000\n Chloe Dubois   |     0\n Kofi Mensah    |  2000",
        },
        {
            "type": "exercise",
            "prompt": "Write a query that shows every employee's bonus, treating a missing bonus as 0 instead of leaving it blank.",
            "starter_code": "SELECT name, ____(bonus, 0) AS bonus\nFROM employees;",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Writing `WHERE bonus = NULL` expecting it to match missing bonuses — it never matches anything, since NULL = NULL isn't true; use `WHERE bonus IS NULL` instead.",
                "Assuming AVG() treats NULL as 0 — it excludes NULL rows entirely from both the sum and the count, which can give a higher average than expected.",
                "Forgetting that concatenating a NULL into a string (in databases where `||` or `+` is used) often produces NULL for the whole result, not just a gap.",
            ],
        },
        {
            "type": "summary",
            "text": "NULL represents unknown, not zero — it's never equal to anything, even itself. COALESCE substitutes a default; aggregates like AVG skip NULLs rather than counting them as zero.",
        },
        {
            "type": "key_terms",
            "items": ["NULL", "COALESCE", "IS NULL", "three-valued logic"],
        },
    ]
}

HYPOTHESIS_TESTING_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "State a null hypothesis and an alternative hypothesis",
                "Explain what a p-value actually measures",
                "Explain the difference between statistical significance and practical importance",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "Hypothesis testing is a formal way of asking \"is this difference real, or could it just be "
                "random noise?\" You assume nothing interesting is happening (the null hypothesis), then check "
                "whether your data would be surprising if that were actually true."
            ),
            "technical": (
                "The p-value is the probability of observing data at least as extreme as what you got, "
                "*assuming the null hypothesis is true* — it is not the probability the null hypothesis is "
                "true, a very common misreading. A small p-value (conventionally < 0.05) means the observed "
                "data would be unusual under the null, so you reject it; it says nothing about the size or "
                "real-world importance of the effect, which is why a huge sample can make a tiny, meaningless "
                "difference statistically significant."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "# Conceptual, not a full test: comparing two group means\n"
                "control = [5.1, 4.9, 5.3, 5.0, 4.8]\n"
                "treatment = [5.6, 5.8, 5.4, 5.9, 5.7]\n\n"
                "control_mean = sum(control) / len(control)\n"
                "treatment_mean = sum(treatment) / len(treatment)\n"
                "print(\"observed difference:\", round(treatment_mean - control_mean, 2))"
            ),
            "output": "observed difference: 0.66",
        },
        {
            "type": "exercise",
            "prompt": "If a hypothesis test on a marketing campaign gives p = 0.03, is that below the conventional 0.05 threshold? Would you reject or fail to reject the null hypothesis?",
            "starter_code": "p_value = 0.03\nthreshold = 0.05\n# reject the null if p_value < threshold\ndecision = \"reject\" if ____ else \"fail to reject\"\nprint(decision)",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Reading a p-value as \"the probability the null hypothesis is true\" — it's the probability of the data given the null, not the probability of the null given the data.",
                "Treating p < 0.05 as proof of a large or important effect — with a big enough sample, even a trivially small difference can be statistically significant.",
                "\"Failing to reject\" the null and concluding it's proven true — a non-significant result just means the data didn't provide strong enough evidence against it, not that there's definitely no effect.",
            ],
        },
        {
            "type": "summary",
            "text": "A p-value is the probability of data this extreme under the null hypothesis, not the probability the null is true. Statistical significance isn't the same as practical importance.",
        },
        {
            "type": "key_terms",
            "items": ["null hypothesis", "alternative hypothesis", "p-value", "statistical significance"],
        },
    ]
}

T_TEST_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Explain what a t-test compares",
                "Distinguish a one-sample t-test from a two-sample t-test",
                "Explain why sample size affects how easily a difference reaches significance",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "A t-test checks whether the difference between two averages is bigger than you'd expect from "
                "random chance alone, given how much the data naturally varies. It's one of the most common "
                "tools for comparing \"did this change actually help?\" style questions."
            ),
            "technical": (
                "The t-statistic is essentially a signal-to-noise ratio: the difference between means, divided "
                "by an estimate of how much that difference would vary by chance (the standard error). A larger "
                "sample shrinks the standard error, which is why the same observed difference can be "
                "non-significant in a small sample and significant in a large one — the test is sensitive to "
                "both effect size and sample size, not effect size alone."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "control = [5.1, 4.9, 5.3, 5.0, 4.8]\n"
                "treatment = [5.6, 5.8, 5.4, 5.9, 5.7]\n\n"
                "def mean(xs):\n"
                "    return sum(xs) / len(xs)\n\n"
                "diff = mean(treatment) - mean(control)\n"
                "print(f\"observed difference: {diff:.2f}\")\n"
                "# A real two-sample t-test (e.g. scipy.stats.ttest_ind) would\n"
                "# turn this difference and the within-group variance into a\n"
                "# t-statistic and p-value — the arithmetic here is the intuition,\n"
                "# not a substitute for the real test."
            ),
            "output": "observed difference: 0.66",
        },
        {
            "type": "exercise",
            "prompt": "Two datasets have the exact same difference in means. Dataset A has 10 observations per group; Dataset B has 1,000. Which is more likely to reach statistical significance, and why?",
            "starter_code": "# Larger samples shrink the standard error for the same\n# observed difference, making the t-statistic ____ (bigger/smaller)\n# and the result more/less likely to be significant.",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Running many t-tests on the same data without correcting for multiple comparisons — each additional test raises the chance of a false positive somewhere, purely by chance.",
                "Using a two-sample t-test on paired data (like before/after measurements on the same people) instead of a paired t-test, which is a different, more appropriate test.",
                "Assuming a significant t-test proves causation — it only shows the means differ more than chance would predict, not why.",
            ],
        },
        {
            "type": "summary",
            "text": "A t-test compares means relative to how much the data naturally varies. It's sensitive to both the size of the effect and the sample size, not effect size alone.",
        },
        {
            "type": "key_terms",
            "items": ["t-test", "t-statistic", "standard error", "two-sample test"],
        },
    ]
}

CORRELATION_CAUSATION_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Compute and interpret a correlation coefficient",
                "Explain why correlation does not imply causation",
                "Identify a plausible confounding variable behind a spurious correlation",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "Correlation measures how strongly two things move together — as one goes up, does the other "
                "tend to go up (or down) too? It says nothing about whether one actually causes the other; two "
                "variables can move together because a third, unmeasured factor is driving both."
            ),
            "technical": (
                "Pearson's correlation coefficient r ranges from -1 (perfect negative) to +1 (perfect "
                "positive), with 0 meaning no linear relationship. A classic confound: ice cream sales and "
                "drowning deaths correlate strongly — not because ice cream causes drowning, but because hot "
                "weather drives both more swimming and more ice cream sales. Establishing causation generally "
                "requires a controlled experiment (randomized assignment) or careful causal-inference methods, "
                "not just a strong correlation in observational data."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "ice_cream_sales = [10, 20, 35, 50, 65]\n"
                "drowning_incidents = [2, 4, 7, 9, 12]\n\n"
                "def mean(xs):\n"
                "    return sum(xs) / len(xs)\n\n"
                "mx, my = mean(ice_cream_sales), mean(drowning_incidents)\n"
                "cov = sum((x - mx) * (y - my) for x, y in zip(ice_cream_sales, drowning_incidents))\n"
                "print(\"positive relationship:\", cov > 0)"
            ),
            "output": "positive relationship: True",
        },
        {
            "type": "exercise",
            "prompt": "Ice cream sales and drowning incidents are positively correlated. Name a plausible confounding variable that could explain both without one causing the other.",
            "starter_code": "confounding_variable = \"____\"  # hint: what changes with the seasons?",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Reporting a correlation and implying causation in the same sentence (\"X increases Y\") without evidence beyond the correlation itself.",
                "Assuming a correlation near 0 means \"no relationship\" — Pearson's r only captures linear relationships; two variables can have a strong curved relationship with r close to 0.",
                "Ignoring an obvious confounder (like season, or overall population size) that plausibly explains both variables moving together.",
            ],
        },
        {
            "type": "summary",
            "text": "Correlation measures how strongly two variables move together, not whether one causes the other. A third, unmeasured confounding variable often explains a correlation better than causation does.",
        },
        {
            "type": "key_terms",
            "items": ["correlation coefficient", "confounding variable", "spurious correlation"],
        },
    ]
}


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        skill_names = {
            "intermediate-python": "Intermediate Python",
            "intermediate-sql": "Intermediate SQL",
            "intermediate-statistics": "Intermediate Statistics",
        }
        skills: dict[str, Skill] = {}
        for slug, name in skill_names.items():
            existing = await db.execute(select(Skill).where(Skill.slug == slug))
            skill = existing.scalar_one_or_none()
            if skill is None:
                category = "python" if "python" in slug else ("sql" if "sql" in slug else "statistics")
                skill = Skill(name=name, slug=slug, category=category)
                db.add(skill)
                await db.flush()
            skills[slug] = skill

        lessons: dict[str, Lesson] = {}

        async def build_course(
            *, title: str, slug: str, description: str, hours: int, module_title: str, module_slug: str,
            lesson_specs: list[tuple[str, str, int, dict, int]], skill_slug: str,
        ) -> Course:
            existing_course = await db.execute(select(Course).where(Course.slug == slug))
            course = existing_course.scalar_one_or_none()
            if course is None:
                course = Course(
                    title=title, slug=slug, description=description,
                    level=LearningLevel.PRACTICAL, estimated_hours=hours, published=True,
                )
                db.add(course)
                await db.flush()
            else:
                course.description = description
                course.estimated_hours = hours

            existing_module = await db.execute(
                select(Module).where(Module.course_id == course.id, Module.slug == module_slug)
            )
            module = existing_module.scalar_one_or_none()
            if module is None:
                module = Module(course_id=course.id, title=module_title, slug=module_slug, order=1)
                db.add(module)
                await db.flush()

            for lesson_slug, lesson_title, order, content, minutes in lesson_specs:
                existing_lesson = await db.execute(
                    select(Lesson).where(Lesson.module_id == module.id, Lesson.slug == lesson_slug)
                )
                lesson = existing_lesson.scalar_one_or_none()
                if lesson is None:
                    lesson = Lesson(
                        module_id=module.id, title=lesson_title, slug=lesson_slug, order=order,
                        content=content, estimated_minutes=minutes, published=True,
                    )
                    db.add(lesson)
                    await db.flush()

                    existing_link = await db.execute(
                        select(LessonSkill).where(
                            LessonSkill.lesson_id == lesson.id, LessonSkill.skill_id == skills[skill_slug].id
                        )
                    )
                    if existing_link.scalar_one_or_none() is None:
                        db.add(LessonSkill(lesson_id=lesson.id, skill_id=skills[skill_slug].id))
                else:
                    lesson.order = order
                lessons[lesson_slug] = lesson

            return course

        py_course = await build_course(
            title="Intermediate Python",
            slug="intermediate-python",
            description="Beyond the basics: comprehensions, files, and handling errors gracefully.",
            hours=3,
            module_title="Practical Python",
            module_slug="practical-python",
            lesson_specs=[
                ("list-comprehensions", "List Comprehensions", 1, LIST_COMPREHENSIONS_CONTENT, 15),
                ("working-with-files", "Working with Files", 2, FILES_CONTENT, 15),
                ("error-handling", "Handling Errors", 3, ERROR_HANDLING_CONTENT, 15),
            ],
            skill_slug="intermediate-python",
        )

        sql_course = await build_course(
            title="Intermediate SQL",
            slug="intermediate-sql",
            description="Window functions, CTEs, and NULL handling — the SQL that separates basic querying from real analysis work.",
            hours=3,
            module_title="Beyond the Basics",
            module_slug="beyond-the-basics",
            lesson_specs=[
                ("window-functions", "Window Functions", 1, WINDOW_FUNCTIONS_CONTENT, 15),
                ("common-table-expressions", "Common Table Expressions", 2, CTE_CONTENT, 15),
                ("null-handling", "NULL Handling", 3, NULL_HANDLING_CONTENT, 15),
            ],
            skill_slug="intermediate-sql",
        )

        stats_course = await build_course(
            title="Intermediate Statistics",
            slug="intermediate-statistics",
            description="From describing data to testing claims about it: hypothesis testing, the t-test, and why correlation isn't causation.",
            hours=3,
            module_title="Inferential Statistics",
            module_slug="inferential-statistics",
            lesson_specs=[
                ("hypothesis-testing", "Hypothesis Testing", 1, HYPOTHESIS_TESTING_CONTENT, 15),
                ("the-t-test", "The t-test", 2, T_TEST_CONTENT, 15),
                ("correlation-vs-causation", "Correlation vs. Causation", 3, CORRELATION_CAUSATION_CONTENT, 15),
            ],
            skill_slug="intermediate-statistics",
        )

        # ---- Quiz on hypothesis testing ----
        existing_quiz = await db.execute(select(Quiz).where(Quiz.lesson_id == lessons["hypothesis-testing"].id))
        quiz = existing_quiz.scalar_one_or_none()
        if quiz is None:
            quiz = Quiz(lesson_id=lessons["hypothesis-testing"].id, title="Hypothesis Testing Check", passing_score=70)
            db.add(quiz)
            await db.flush()
            db.add_all(
                [
                    QuizQuestion(
                        quiz_id=quiz.id,
                        question_text="A p-value of 0.03 means:",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options={
                            "choices": [
                                "There's a 3% chance the null hypothesis is true",
                                "Data this extreme has a 3% chance of occurring if the null hypothesis is true",
                                "The effect is definitely real and important",
                                "97% of the variance is explained",
                            ]
                        },
                        correct_answer={"value": "Data this extreme has a 3% chance of occurring if the null hypothesis is true"},
                        explanation="A p-value is P(data | null hypothesis true), not P(null hypothesis true | data).",
                        order=1,
                        points=1,
                    ),
                    QuizQuestion(
                        quiz_id=quiz.id,
                        question_text="Statistical significance always means the effect is practically important.",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options={"choices": ["True", "False"]},
                        correct_answer={"value": "False"},
                        explanation="A large enough sample can make a tiny, unimportant difference statistically significant.",
                        order=2,
                        points=1,
                    ),
                ]
            )

        # ---- Quiz on window functions ----
        existing_wf_quiz = await db.execute(select(Quiz).where(Quiz.lesson_id == lessons["window-functions"].id))
        wf_quiz = existing_wf_quiz.scalar_one_or_none()
        if wf_quiz is None:
            wf_quiz = Quiz(lesson_id=lessons["window-functions"].id, title="Window Functions Check", passing_score=70)
            db.add(wf_quiz)
            await db.flush()
            db.add_all(
                [
                    QuizQuestion(
                        quiz_id=wf_quiz.id,
                        question_text="Unlike GROUP BY, a window function:",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options={
                            "choices": [
                                "Collapses rows into one per group",
                                "Keeps every original row while still computing a per-group value",
                                "Can only be used with COUNT",
                                "Requires a subquery to work at all",
                            ]
                        },
                        correct_answer={"value": "Keeps every original row while still computing a per-group value"},
                        explanation="Window functions compute across a partition without reducing the row count, unlike GROUP BY.",
                        order=1,
                        points=1,
                    ),
                    QuizQuestion(
                        quiz_id=wf_quiz.id,
                        question_text="Which clause defines the group of rows a window function operates over?",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options={"choices": ["GROUP BY", "PARTITION BY", "HAVING", "WHERE"]},
                        correct_answer={"value": "PARTITION BY"},
                        explanation="PARTITION BY, inside OVER(), defines the window for the function.",
                        order=2,
                        points=1,
                    ),
                ]
            )

        # ---- Add both new courses to the learning path ----
        existing_path = await db.execute(select(LearningPath).where(LearningPath.slug == "data-analytics-foundations"))
        path = existing_path.scalar_one_or_none()
        if path is not None:
            for course, order in [(py_course, 5), (sql_course, 6), (stats_course, 7)]:
                existing_lpc = await db.execute(
                    select(LearningPathCourse).where(
                        LearningPathCourse.learning_path_id == path.id, LearningPathCourse.course_id == course.id
                    )
                )
                if existing_lpc.scalar_one_or_none() is None:
                    db.add(LearningPathCourse(learning_path_id=path.id, course_id=course.id, order=order))

        await db.commit()
        print("Seed complete: 3 skills, 3 courses (3 lessons each = 9 lessons), 2 quizzes, added to learning path.")


if __name__ == "__main__":
    asyncio.run(seed())
