"""Seeds the interview question bank (P2 roadmap item). Idempotent — safe
to re-run. Run: python3 scripts/seed_interview_questions.py
"""

import asyncio

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.base import LearningLevel
from app.models.career import CareerPath, InterviewQuestion

B = LearningLevel.BEGINNER
P = LearningLevel.PRACTICAL
T = LearningLevel.TECHNICAL
A = LearningLevel.ADVANCED
PR = LearningLevel.PROFESSIONAL

# (question, category, difficulty, sample_answer, career_path_slug_or_None)
QUESTIONS = [
    (
        "What's the difference between WHERE and HAVING?",
        "SQL",
        B,
        "WHERE filters individual rows before grouping/aggregation; HAVING filters groups after aggregation, "
        "so it can reference aggregate functions like COUNT() or SUM() that WHERE can't see yet.",
        None,
    ),
    (
        "Explain the difference between INNER JOIN and LEFT JOIN.",
        "SQL",
        P,
        "INNER JOIN returns only rows that have a match in both tables. LEFT JOIN returns every row from the "
        "left table regardless of a match, filling unmatched right-side columns with NULL.",
        None,
    ),
    (
        "How would you find the second-highest salary in a table without using LIMIT/OFFSET?",
        "SQL",
        T,
        "Use a window function: SELECT salary FROM (SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS "
        "rnk FROM employees) t WHERE rnk = 2. DENSE_RANK handles ties correctly, unlike a naive "
        "'MAX() less than the overall MAX()' approach which can skip valid answers.",
        "data-analyst",
    ),
    (
        "What's the difference between UNION and UNION ALL?",
        "SQL",
        T,
        "UNION removes duplicate rows across the combined result, which requires an implicit sort/dedup step and "
        "is slower. UNION ALL keeps every row including duplicates and is faster since it skips that step.",
        None,
    ),
    (
        "Why might a query with a function applied to an indexed column, like WHERE YEAR(created_at) = 2026, "
        "perform poorly?",
        "SQL",
        A,
        "Wrapping the column in a function usually prevents the query planner from using an index on that "
        "column, forcing a full table scan. Rewriting it as a range condition — created_at >= '2026-01-01' AND "
        "created_at < '2027-01-01' — lets the index be used again.",
        "data-engineer",
    ),
    (
        "How do you design a query to deduplicate rows while keeping only the most recent one per key?",
        "SQL",
        PR,
        "Rank rows within each key by recency with a window function, then filter to rank 1: SELECT * FROM "
        "(SELECT *, ROW_NUMBER() OVER (PARTITION BY key ORDER BY updated_at DESC) AS rn FROM t) sub WHERE rn = 1.",
        "data-engineer",
    ),
    (
        "What's the difference between a list and a tuple in Python?",
        "Python",
        B,
        "Lists are mutable — they can be changed after creation. Tuples are immutable, slightly faster to "
        "iterate, and can be used as dictionary keys or set members, which mutable lists can't.",
        None,
    ),
    (
        "What does `is` check for, compared to `==`?",
        "Python",
        B,
        "== checks value equality (do these two things look the same). `is` checks identity — whether two names "
        "point to the exact same object in memory.",
        None,
    ),
    (
        "Why is a mutable default argument, like def f(x, items=[]), considered a bug risk?",
        "Python",
        P,
        "The default list is created once, when the function is defined, not on each call — so mutations to it "
        "persist across calls and silently leak state between unrelated invocations.",
        None,
    ),
    (
        "What's the difference between a list comprehension and a generator expression?",
        "Python",
        T,
        "A list comprehension builds the entire list in memory immediately. A generator expression (written with "
        "parentheses instead of brackets) produces values lazily, one at a time, which saves memory on large or "
        "unbounded sequences.",
        None,
    ),
    (
        "Explain Python's GIL and why it matters for data science workloads.",
        "Python",
        T,
        "The Global Interpreter Lock allows only one thread to execute Python bytecode at a time, so CPU-bound "
        "multithreading doesn't get true parallelism. Libraries like NumPy and pandas release the GIL during "
        "heavy C-level operations, and multiprocessing sidesteps it entirely by using separate processes.",
        "data-scientist",
    ),
    (
        "What's the difference between a shallow copy and a deep copy?",
        "Python",
        A,
        "A shallow copy creates a new outer object but still references the same nested objects as the "
        "original. A deep copy recursively copies nested objects too, so changes to nested data in the copy "
        "don't affect the original.",
        None,
    ),
    (
        "What's the difference between population and sample standard deviation?",
        "Statistics",
        B,
        "Population standard deviation divides the sum of squared deviations by N. Sample standard deviation "
        "divides by N-1 (Bessel's correction), which corrects for the bias of estimating variance from a "
        "sample rather than the whole population.",
        None,
    ),
    (
        "Why can the mean be a misleading summary of income data?",
        "Statistics",
        B,
        "Income distributions are right-skewed with a long tail of very high earners, which pulls the mean up. "
        "The median better represents a 'typical' income because it isn't dragged by extreme values.",
        "data-analyst",
    ),
    (
        "What's the difference between a Type I error and a Type II error?",
        "Statistics",
        P,
        "A Type I error is a false positive — rejecting a true null hypothesis. A Type II error is a false "
        "negative — failing to reject a null hypothesis that's actually false.",
        None,
    ),
    (
        "What assumptions does a standard linear regression rely on?",
        "Statistics",
        T,
        "Linearity between predictors and the outcome, independence of errors, homoscedasticity (constant error "
        "variance across predictions), and normally distributed residuals. Violating these doesn't make the "
        "model useless, but it undermines the validity of its p-values and confidence intervals.",
        "data-scientist",
    ),
    (
        "What's the difference between correlation and causation, and how would you argue for causation from "
        "observational data?",
        "Statistics",
        T,
        "Correlation means two variables move together; causation means one directly influences the other. "
        "Arguing for causation from observational data means ruling out confounders and reverse causation — via "
        "techniques like natural experiments, instrumental variables, or matching — rather than pointing at the "
        "correlation alone.",
        "data-analyst",
    ),
    (
        "Explain the bias-variance tradeoff.",
        "Statistics",
        A,
        "Bias is error from overly simplistic assumptions (underfitting). Variance is error from sensitivity to "
        "the specific training data (overfitting). Reducing one often increases the other, so model selection "
        "is about finding the balance that minimizes total expected error on unseen data.",
        "data-scientist",
    ),
    (
        "How do you check for missing values in a pandas DataFrame?",
        "Pandas",
        B,
        "df.isna().sum() gives a per-column count of missing values across the whole DataFrame.",
        None,
    ),
    (
        "What's the difference between .loc and .iloc in pandas?",
        "Pandas",
        P,
        ".loc selects by label — index or column names. .iloc selects by integer position, regardless of what "
        "the labels actually are.",
        "data-analyst",
    ),
    (
        "Why can chained indexing, like df[df.a > 0]['b'] = 5, fail silently in pandas?",
        "Pandas",
        T,
        "It can trigger pandas' SettingWithCopyWarning, because the intermediate result of df[df.a > 0] may be "
        "a copy rather than a view — so the assignment might not actually modify the original DataFrame. Use "
        "df.loc[df.a > 0, 'b'] = 5 instead, which is unambiguous.",
        None,
    ),
    (
        "How would you merge two large DataFrames efficiently when one is a much smaller lookup table?",
        "Pandas",
        T,
        "Filter the larger frame down first if possible, consider setting the join key as the index on both "
        "sides before merging, and use merge (not concat) for key-based joins — concat with axis=1 assumes "
        "already-aligned indexes rather than matching on a key.",
        None,
    ),
    (
        "Tell me about a time you found an error in your own analysis after presenting it. What did you do?",
        "Behavioral",
        B,
        "Look for: how the error was caught, concrete steps taken to correct it and communicate the correction "
        "transparently rather than quietly, and what changed in their process afterward — like adding a "
        "validation step — to reduce the chance of a repeat.",
        None,
    ),
    (
        "How do you communicate a technical finding to a non-technical stakeholder?",
        "Behavioral",
        P,
        "Lead with the business implication before the method, translate jargon immediately rather than "
        "avoiding it, favor a concrete visual over a table of numbers, and state uncertainty in plain language "
        "instead of statistical terms.",
        None,
    ),
    (
        "Describe a time a stakeholder disagreed with your analysis. How did you handle it?",
        "Behavioral",
        P,
        "Look for genuine engagement with their reasoning rather than dismissing it, checking whether the "
        "pushback revealed a real gap in the analysis, and reaching a resolution grounded in evidence rather "
        "than authority or seniority.",
        None,
    ),
    (
        "How do you prioritize when you have multiple competing data requests?",
        "Behavioral",
        T,
        "Look for weighing business impact and urgency explicitly, communicating tradeoffs and timelines to "
        "stakeholders rather than silently picking one, and revisiting priorities as new information arrives.",
        None,
    ),
    (
        "Daily active users dropped 10% overnight. How would you investigate?",
        "Case Study",
        P,
        "Check for a tracking or instrumentation bug first — the most common cause of a sudden overnight drop — "
        "then segment by platform, region, and cohort to see if the drop is broad or localized, check for a bad "
        "deploy or outage, and only then consider genuine behavioral causes.",
        "data-analyst",
    ),
    (
        "How would you design an A/B test to measure whether a new feature increases user retention?",
        "Case Study",
        T,
        "Define retention precisely (e.g., D7 return rate), randomize at a stable unit — usually user ID, not "
        "session — compute the required sample size from a minimum detectable effect and desired power, run for "
        "a full business cycle to avoid novelty effects, and pre-register the primary metric to avoid "
        "p-hacking across many secondary metrics.",
        "data-scientist",
    ),
    (
        "An A/B test shows a statistically significant lift, but the product team is skeptical. What do you "
        "check?",
        "Case Study",
        T,
        "Check for sample ratio mismatch — verifying the control/treatment split matches the intended ratio — "
        "check for novelty effects if the test ran too briefly, check for multiple-comparisons inflation if "
        "many metrics were tested, and confirm the effect size is practically meaningful, not just "
        "statistically significant.",
        "data-scientist",
    ),
    (
        "How would you decide whether to build a churn-prediction model versus using simpler rule-based flags?",
        "Case Study",
        A,
        "Compare against a baseline: how well do simple rules (e.g., no login in 30 days) already perform on "
        "precision/recall for the actual business use case, then weigh the model's added lift against its "
        "cost — deployment complexity, retraining, and the explainability required by whoever acts on its "
        "predictions.",
        "ml-engineer",
    ),
]


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        career_paths = {cp.slug: cp for cp in (await db.execute(select(CareerPath))).scalars().all()}

        added = 0
        for question, category, difficulty, sample_answer, career_path_slug in QUESTIONS:
            existing = await db.execute(select(InterviewQuestion).where(InterviewQuestion.question == question))
            if existing.scalar_one_or_none() is not None:
                continue
            career_path = career_paths.get(career_path_slug) if career_path_slug else None
            db.add(
                InterviewQuestion(
                    question=question,
                    category=category,
                    difficulty=difficulty,
                    sample_answer=sample_answer,
                    career_path_id=career_path.id if career_path else None,
                )
            )
            added += 1

        await db.commit()
        print(f"Seed complete: added {added} new interview questions (of {len(QUESTIONS)} total defined).")


if __name__ == "__main__":
    asyncio.run(seed())
