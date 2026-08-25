"""Seeds achievement definitions and a small set of real flashcards tied to
the skills seeded in Phase 5. Run: python3 scripts/seed_gamification.py
"""

import asyncio

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.curriculum import Skill
from app.models.gamification import Achievement
from app.models.learning_science import Flashcard
from app.services.gamification_service import ACHIEVEMENT_DEFINITIONS

FLASHCARDS = [
    ("python-fundamentals", "What does `=` do in Python?", "Binds a name to an object — assignment, not comparison."),
    ("python-fundamentals", "What error do you get from using a variable before assigning it?", "NameError"),
    ("python-fundamentals", "Which operator checks equality?", "== (double equals)"),
    ("python-fundamentals", "What index does the first item in a Python list have?", "0 — lists are zero-indexed."),
    ("python-fundamentals", "How many branches of an if/elif/else chain run?", "Exactly one (or none, if nothing matches and there's no else)."),
    ("python-fundamentals", "What does a function return if it has no `return` statement?", "None"),
    ("python-fundamentals", "What's the difference between `print(x)` and `return x` inside a function?", "print only displays text and gives back None; return hands the value to the caller so it can be used."),
    ("pandas-dataframes", "What does `df[\"col\"]` return: a DataFrame or a Series?", "A Series — use `df[[\"col\"]]` (double brackets) to keep it as a DataFrame."),
    ("pandas-dataframes", "How do you filter rows where a column exceeds 100?", "df[df[\"col\"] > 100]"),
    ("pandas-dataframes", "What library is a pandas DataFrame built on top of?", "NumPy"),
    ("sql-fundamentals", "What SQL clause guarantees a specific row order in the results?", "ORDER BY — without it, row order isn't guaranteed."),
    ("sql-fundamentals", "How do you check for a missing value in SQL — `= NULL` or `IS NULL`?", "IS NULL — NULL is never equal to anything, even itself."),
    ("sql-fundamentals", "What happens if you JOIN two tables without an ON condition?", "A cross join — every row from one table pairs with every row from the other."),
    ("sql-fundamentals", "Does an INNER JOIN include rows that have no match in the other table?", "No — only rows that match in both tables. LEFT JOIN is what keeps unmatched rows."),
    ("sql-fundamentals", "Which SQL clause filters rows after aggregation, so it can reference COUNT(*)?", "HAVING — WHERE runs before grouping and can't see aggregates yet."),
    ("statistics-fundamentals", "Why does the median resist outliers better than the mean?", "The mean is pulled by every value; the median only cares about the middle rank, so one extreme value barely moves it."),
    ("statistics-fundamentals", "For independent events, how do you compute P(A and B)?", "P(A) × P(B)"),
    ("statistics-fundamentals", "What does a z-score measure?", "How many standard deviations a value is from the mean."),
    ("statistics-fundamentals", "Roughly what percentage of values fall within 2 standard deviations of the mean in a normal distribution?", "About 95% (the 68-95-99.7 rule)."),
    ("pandas-wrangling", "What does how=\"left\" keep in a pandas merge that how=\"inner\" would drop?", "Every row from the left DataFrame, even ones with no match on the right (filled with NaN)."),
    ("pandas-wrangling", "Does df.groupby(\"col\") compute anything by itself?", "No — it's lazy. You need an aggregate like .mean() or .agg() to actually compute a result."),
    ("pandas-wrangling", "What's the difference between dropna() and fillna()?", "dropna() removes rows/columns with missing values; fillna() replaces them with a given value."),
    ("intermediate-python", "What's the syntax for a list comprehension that filters?", "[expr for item in iterable if condition]"),
    ("intermediate-python", "Why prefer `with open(path) as f:` over a plain open()/close()?", "with guarantees the file is closed even if an exception is raised inside the block."),
    ("intermediate-python", "Why is a bare `except:` usually a mistake?", "It catches everything, including bugs you didn't anticipate (like a NameError from a typo), making failures harder to find."),
    ("intermediate-sql", "What does PARTITION BY do inside a window function?", "Defines the group of rows the function computes over, without collapsing them into one row per group like GROUP BY does."),
    ("intermediate-sql", "What's the main readability advantage of a CTE (WITH clause) over nested subqueries?", "It breaks a complex query into named, sequential steps instead of nesting queries inside each other."),
    ("intermediate-sql", "Does AVG() treat NULL values as 0?", "No — it excludes NULL rows entirely from both the sum and the count."),
    ("intermediate-statistics", "What does a p-value of 0.03 actually mean?", "There's a 3% chance of seeing data this extreme if the null hypothesis is true — not a 3% chance the null hypothesis is true."),
    ("intermediate-statistics", "Why can a large sample make a tiny, unimportant difference statistically significant?", "Larger samples shrink the standard error, so even a small real difference becomes easier to distinguish from noise."),
    ("intermediate-statistics", "Ice cream sales and drowning deaths are correlated. What explains this without one causing the other?", "A confounding variable — hot weather drives both more swimming and more ice cream sales."),
]


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        for definition in ACHIEVEMENT_DEFINITIONS:
            existing = await db.execute(select(Achievement).where(Achievement.key == definition["key"]))
            if existing.scalar_one_or_none() is None:
                db.add(
                    Achievement(
                        key=definition["key"],
                        name=definition["name"],
                        description=definition["description"],
                        xp_reward=definition["xp_reward"],
                        icon=definition["icon"],
                        criteria={"type": "real_activity_count", "min": 1},
                    )
                )

        for skill_slug, front, back in FLASHCARDS:
            skill_result = await db.execute(select(Skill).where(Skill.slug == skill_slug))
            skill = skill_result.scalar_one_or_none()
            if skill is None:
                continue
            existing = await db.execute(select(Flashcard).where(Flashcard.front == front))
            if existing.scalar_one_or_none() is None:
                db.add(Flashcard(skill_id=skill.id, front=front, back=back))

        await db.commit()
        print(f"Seed complete: {len(ACHIEVEMENT_DEFINITIONS)} achievements, up to {len(FLASHCARDS)} flashcards.")


if __name__ == "__main__":
    asyncio.run(seed())
