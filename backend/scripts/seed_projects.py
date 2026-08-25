"""Idempotent project seed — two real, original project briefs matching the
Project Factory output shape from Phase 1 §31 (business problem,
objectives, steps, deliverables, evaluation rubric). Hand-written, not
generated, since the actual generative wizard from §31 isn't built yet —
this proves the data model and UI with genuine content.

Run: python3 scripts/seed_projects.py
"""

import asyncio

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.base import DifficultyLevel
from app.models.projects import Project, ProjectType

PROJECTS = [
    dict(
        title="Income Survey EDA",
        slug="income-survey-eda",
        description="Explore a small, messy income survey — the kind of first-pass data cleaning and exploration every analyst does before any modeling.",
        difficulty=DifficultyLevel.BEGINNER,
        project_type=ProjectType.EDA,
        rubric={
            "business_problem": (
                "A researcher collected a small income survey but the data has gaps and at "
                "least one suspicious value. Before anyone can draw conclusions from it, it "
                "needs a proper exploratory pass."
            ),
            "objectives": [
                "Identify and quantify missing data",
                "Detect and reason about outliers rather than blindly removing them",
                "Summarize the relationship between age and income",
            ],
            "questions": [
                "Which columns have missing values, and how much?",
                "Is the highest income value a data entry error or a real outlier?",
                "Does income correlate with age in this sample?",
            ],
            "skills": ["python-fundamentals", "pandas-dataframes"],
            "tools": ["Python Lab", "Datasets → EDA profiling"],
            "steps": [
                "Upload a CSV (or use the Datasets page's built-in profiling) and review the missing-value and outlier summary",
                "Decide, with reasoning, what to do about the missing age/income values",
                "Compute the correlation between age and income and interpret it in one paragraph",
                "Write a 3-bullet summary of what you'd tell a stakeholder before they see the raw numbers",
            ],
            "deliverables": [
                "A short written summary (not just numbers) of data quality issues found",
                "A documented decision on how missing/outlier values were handled, with reasoning",
            ],
            "evaluation_rubric": {
                "identifies_missing_data": "Correctly reports which columns are missing and how much",
                "reasons_about_outliers": "Does not just delete the outlier without justification",
                "communicates_clearly": "Summary is understandable to a non-technical stakeholder",
            },
        },
    ),
    dict(
        title="Departmental Salary Analysis",
        slug="departmental-salary-analysis",
        description="Use SQL to answer real questions a People Ops team would actually ask about departmental pay.",
        difficulty=DifficultyLevel.BEGINNER,
        project_type=ProjectType.SQL_ANALYSIS,
        rubric={
            "business_problem": (
                "People Operations wants a quick pulse check on departmental compensation "
                "before the next budgeting cycle: which departments are best-funded relative to "
                "headcount, and how does tenure relate to pay?"
            ),
            "objectives": [
                "Practice JOINs across a real (if small) relational schema",
                "Practice GROUP BY aggregation for business reporting",
                "Translate a business question into a precise SQL query",
            ],
            "questions": [
                "What is the average salary per department?",
                "Which department has the highest budget-per-employee?",
                "Do longer-tenured employees earn more, on average, in this sample?",
            ],
            "skills": ["sql-select"],
            "tools": ["SQL Lab"],
            "steps": [
                "Open the SQL Lab and work through its four built-in exercises first",
                "Write a query joining employees and departments to compute average salary per department",
                "Write a query computing budget ÷ headcount per department",
                "Write a one-paragraph interpretation of what you found",
            ],
            "deliverables": [
                "Three working SQL queries answering the three questions above",
                "A short written interpretation of the results",
            ],
            "evaluation_rubric": {
                "correct_joins": "JOINs produce the correct row set, no fan-out duplication",
                "correct_aggregation": "GROUP BY results match manual verification",
                "interpretation": "Conclusions are actually supported by the query results",
            },
        },
    ),
]


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        for spec in PROJECTS:
            existing = await db.execute(select(Project).where(Project.slug == spec["slug"]))
            if existing.scalar_one_or_none() is None:
                db.add(Project(**spec))
        await db.commit()
        print(f"Seed complete: {len(PROJECTS)} projects.")


if __name__ == "__main__":
    asyncio.run(seed())
