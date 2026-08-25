"""Idempotent seed for the Resources library and Glossary — both tables
existed with a real model and zero rows/API before this. Every resource URL
below was fetched and visually confirmed live on 2026-08-25 (not recalled
from training data) before being added here.

Run: python3 scripts/seed_resources.py
"""

import asyncio
from datetime import date

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.base import LearningLevel
from app.models.knowledge_base import GlossaryTerm, Resource

VERIFIED_ON = date(2026, 8, 25)

RESOURCES = [
    {
        "title": "pandas Documentation",
        "provider": "pandas / NumFOCUS",
        "level": LearningLevel.PRACTICAL,
        "is_free": True,
        "description": "The official pandas docs — getting-started guides, the full user guide, and API reference. The canonical source once you're past the basics taught here.",
        "url": "https://pandas.pydata.org/docs/",
    },
    {
        "title": "The Python Tutorial",
        "provider": "Python Software Foundation",
        "level": LearningLevel.BEGINNER,
        "is_free": True,
        "description": "The official Python tutorial — a thorough, sixteen-chapter walkthrough of the language from a beginner's first program through modules and virtual environments.",
        "url": "https://docs.python.org/3/tutorial/",
    },
    {
        "title": "PostgreSQL Tutorial",
        "provider": "PostgreSQL Global Development Group",
        "level": LearningLevel.PRACTICAL,
        "is_free": True,
        "description": "The official PostgreSQL tutorial — relational database concepts and SQL from first principles, straight from the source that runs the SQL Lab here.",
        "url": "https://www.postgresql.org/docs/current/tutorial.html",
    },
    {
        "title": "Kaggle Learn",
        "provider": "Kaggle",
        "level": LearningLevel.BEGINNER,
        "is_free": True,
        "description": "Short, free, hands-on courses (Python, Pandas, Data Visualization, and more), each with in-browser coding exercises graded automatically.",
        "url": "https://www.kaggle.com/learn",
    },
    {
        "title": "Statistics and Probability",
        "provider": "Khan Academy",
        "level": LearningLevel.BEGINNER,
        "is_free": True,
        "description": "A full free course covering descriptive statistics, probability, and distributions with video lessons and practice problems — good companion to the Statistics Fundamentals course here.",
        "url": "https://www.khanacademy.org/math/statistics-probability",
    },
    {
        "title": "SQL Tutorial",
        "provider": "W3Schools",
        "level": LearningLevel.BEGINNER,
        "is_free": True,
        "description": "A reference-style SQL tutorial with an in-browser \"Try it Yourself\" editor for every clause — useful for quick lookups while working in the SQL Lab.",
        "url": "https://www.w3schools.com/sql/",
    },
    {
        "title": "Real Python",
        "provider": "Real Python",
        "level": LearningLevel.PRACTICAL,
        "is_free": True,
        "description": "In-depth Python tutorials and articles spanning beginner to advanced topics, including pandas, data science, and best practices. Some content is subscriber-only.",
        "url": "https://realpython.com/",
    },
    {
        "title": "Data Analysis with Python Certification",
        "provider": "freeCodeCamp",
        "level": LearningLevel.PRACTICAL,
        "is_free": True,
        "description": "A free, project-based certification covering NumPy, pandas, Matplotlib, and Seaborn, ending in five real data-analysis projects.",
        "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/",
    },
]

GLOSSARY_TERMS = [
    {
        "term": "Variable",
        "slug": "variable",
        "simple_explanation": "A name you give to a piece of data so you can use it again later.",
        "technical_explanation": "A name bound to an object in memory. Assignment points the name at an object rather than copying data into a fixed box.",
        "example": "age = 29 binds the name age to the integer object 29.",
    },
    {
        "term": "DataFrame",
        "slug": "dataframe",
        "simple_explanation": "pandas' table object — rows and columns, like a spreadsheet, that you can filter and calculate on with code.",
        "technical_explanation": "A 2-dimensional, size-mutable, labeled data structure whose columns can each hold a different dtype, built on top of NumPy arrays.",
        "example": "pd.DataFrame({\"name\": [\"Amara\"], \"score\": [88]})",
    },
    {
        "term": "JOIN",
        "slug": "join",
        "simple_explanation": "Combines rows from two tables that share a common value, so you can query them as one.",
        "technical_explanation": "An INNER JOIN returns only rows where the join condition matches in both tables; LEFT/RIGHT/OUTER JOIN keep some or all unmatched rows too.",
        "example": "SELECT e.name, d.name FROM employees e JOIN departments d ON e.department_id = d.id",
    },
    {
        "term": "GROUP BY",
        "slug": "group-by",
        "simple_explanation": "Splits rows into buckets by a category so you can compute one value per bucket, like a subtotal per group.",
        "technical_explanation": "Partitions the result set by the grouping column(s); every selected column must be either grouped or wrapped in an aggregate function.",
        "example": "SELECT department_id, AVG(salary) FROM employees GROUP BY department_id",
    },
    {
        "term": "Mean",
        "slug": "mean",
        "simple_explanation": "The arithmetic average — add everything up, divide by how many there are.",
        "technical_explanation": "Sensitive to outliers, since every value pulls it, weighted equally. Contrast with the median, which only depends on rank.",
        "example": "The mean of [1, 2, 3, 100] is 26.5, even though most of the values are small.",
    },
    {
        "term": "Median",
        "slug": "median",
        "simple_explanation": "The middle value once all the data is sorted.",
        "technical_explanation": "An order statistic — it only depends on rank, so a single extreme value barely moves it, unlike the mean.",
        "example": "The median of [1, 2, 3, 100] is 2.5, far more representative of the typical value than the mean.",
    },
    {
        "term": "Standard Deviation",
        "simple_explanation": "A number that measures how spread out data is around the mean.",
        "slug": "standard-deviation",
        "technical_explanation": "The square root of variance — the average squared deviation from the mean, back in the original units.",
        "example": "Two datasets can share the same mean but have very different standard deviations if one is far more spread out.",
    },
    {
        "term": "z-score",
        "slug": "z-score",
        "simple_explanation": "How many standard deviations a value sits above or below the average.",
        "technical_explanation": "Computed as (x − mean) / standard deviation. Standardizes values so they're comparable across different distributions.",
        "example": "A test score with z = 2.0 is 2 standard deviations above the average score.",
    },
    {
        "term": "NaN",
        "slug": "nan",
        "simple_explanation": "pandas' way of representing a missing value in your data.",
        "technical_explanation": "Short for 'Not a Number'. Most pandas aggregate methods skip NaN by default; isna()/dropna()/fillna() are the standard tools for handling it.",
        "example": "pd.DataFrame({\"score\": [88, None]})[\"score\"] shows the second value as NaN.",
    },
    {
        "term": "Subquery",
        "slug": "subquery",
        "simple_explanation": "A query nested inside another query, used to answer a bigger question with a smaller one's result.",
        "technical_explanation": "Runs first (once for an uncorrelated subquery, or once per outer row for a correlated one) and feeds its result into the outer query's condition.",
        "example": "SELECT name FROM employees WHERE salary > (SELECT AVG(salary) FROM employees)",
    },
]


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        added_resources = 0
        for r in RESOURCES:
            existing = await db.execute(select(Resource).where(Resource.url == r["url"]))
            if existing.scalar_one_or_none() is None:
                db.add(Resource(**r, last_verified_at=VERIFIED_ON))
                added_resources += 1

        added_terms = 0
        for t in GLOSSARY_TERMS:
            existing = await db.execute(select(GlossaryTerm).where(GlossaryTerm.slug == t["slug"]))
            if existing.scalar_one_or_none() is None:
                db.add(GlossaryTerm(**t))
                added_terms += 1

        await db.commit()
        print(f"Seed complete: {added_resources} resources added (of {len(RESOURCES)}), {added_terms} glossary terms added (of {len(GLOSSARY_TERMS)}).")


if __name__ == "__main__":
    asyncio.run(seed())
