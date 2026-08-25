"""Idempotent seed for the 6 career paths named in Phase 1 §16/§45, each
mapped to the skills that actually exist in the curriculum today
(python-fundamentals, pandas-dataframes, pandas-wrangling,
sql-fundamentals, statistics-fundamentals). Weights are a genuine,
considered relative emphasis per track — not fabricated per-path
differentiation on skills the curriculum doesn't have yet. As more skills
are added (visualization, ML, etc.) each path's weights should be
revisited; this seed is a real starting point, not a finished taxonomy.

Run: python3 scripts/seed_career_paths.py
(Requires the skills seeded by seed_curriculum.py and
seed_curriculum_stats_wrangling.py to already exist.)
"""

import asyncio

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.career import CareerPath, CareerPathSkill
from app.models.curriculum import Skill

CAREER_PATHS = [
    {
        "name": "Data Analyst",
        "slug": "data-analyst",
        "description": "Turns raw data into decisions: querying databases, cleaning data, and building reports that answer real business questions.",
        "weights": {
            "sql-fundamentals": 3.0,
            "pandas-dataframes": 2.0,
            "pandas-wrangling": 2.0,
            "statistics-fundamentals": 2.0,
            "python-fundamentals": 1.5,
        },
    },
    {
        "name": "Data Scientist",
        "slug": "data-scientist",
        "description": "Builds statistical and predictive models to answer open-ended questions, leaning heavily on Python, statistics, and experimentation.",
        "weights": {
            "statistics-fundamentals": 3.0,
            "python-fundamentals": 2.5,
            "pandas-dataframes": 2.5,
            "pandas-wrangling": 2.5,
            "sql-fundamentals": 1.5,
        },
    },
    {
        "name": "Data Engineer",
        "slug": "data-engineer",
        "description": "Builds and maintains the pipelines and infrastructure that move and transform data reliably at scale.",
        "weights": {
            "sql-fundamentals": 3.0,
            "python-fundamentals": 2.5,
            "pandas-wrangling": 1.5,
            "pandas-dataframes": 1.0,
            "statistics-fundamentals": 1.0,
        },
    },
    {
        "name": "ML Engineer",
        "slug": "ml-engineer",
        "description": "Takes models from notebook to production: strong programming fundamentals paired with a solid statistics foundation.",
        "weights": {
            "python-fundamentals": 3.0,
            "statistics-fundamentals": 2.5,
            "pandas-dataframes": 2.0,
            "pandas-wrangling": 2.0,
            "sql-fundamentals": 1.5,
        },
    },
    {
        "name": "Analytics Engineer",
        "slug": "analytics-engineer",
        "description": "Sits between data engineering and analytics: modeling clean, well-tested datasets that analysts and dashboards can trust.",
        "weights": {
            "sql-fundamentals": 3.0,
            "pandas-wrangling": 2.5,
            "python-fundamentals": 2.0,
            "pandas-dataframes": 1.5,
            "statistics-fundamentals": 1.0,
        },
    },
    {
        "name": "BI Analyst",
        "slug": "bi-analyst",
        "description": "Builds dashboards and reporting that make business metrics visible and trustworthy across an organization.",
        "weights": {
            "sql-fundamentals": 3.0,
            "statistics-fundamentals": 2.0,
            "pandas-dataframes": 1.5,
            "pandas-wrangling": 1.0,
            "python-fundamentals": 1.0,
        },
    },
]


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        skills_result = await db.execute(select(Skill))
        skills_by_slug = {s.slug: s for s in skills_result.scalars().all()}

        added_paths = 0
        added_links = 0
        for spec in CAREER_PATHS:
            existing = await db.execute(select(CareerPath).where(CareerPath.slug == spec["slug"]))
            career_path = existing.scalar_one_or_none()
            if career_path is None:
                career_path = CareerPath(name=spec["name"], slug=spec["slug"], description=spec["description"])
                db.add(career_path)
                await db.flush()
                added_paths += 1

            for skill_slug, weight in spec["weights"].items():
                skill = skills_by_slug.get(skill_slug)
                if skill is None:
                    continue
                existing_link = await db.execute(
                    select(CareerPathSkill).where(
                        CareerPathSkill.career_path_id == career_path.id, CareerPathSkill.skill_id == skill.id
                    )
                )
                if existing_link.scalar_one_or_none() is None:
                    db.add(CareerPathSkill(career_path_id=career_path.id, skill_id=skill.id, weight=weight))
                    added_links += 1

        await db.commit()
        print(f"Seed complete: {added_paths} career paths added (of {len(CAREER_PATHS)}), {added_links} skill weightings added.")


if __name__ == "__main__":
    asyncio.run(seed())
