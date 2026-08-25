"""Idempotent curriculum seed — the next layer of the exhaustive curriculum
beyond Python/SQL fundamentals: "Statistics Fundamentals" (3 lessons) and
"Data Wrangling with pandas" (3 lessons), both added to the existing
"Data Analytics Foundations" learning path alongside the Python and SQL
courses seeded by seed_curriculum.py.

Run: python3 scripts/seed_curriculum_stats_wrangling.py
(Run seed_curriculum.py first — this reuses that script's learning path.)
"""

import asyncio

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.assessment import QuestionType, Quiz, QuizQuestion
from app.models.base import LearningLevel
from app.models.curriculum import Course, LearningPath, LearningPathCourse, Lesson, LessonSkill, Module, Skill

DESCRIPTIVE_STATS_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Compute and distinguish mean, median, and mode",
                "Explain why the median resists outliers better than the mean",
                "Compute variance and standard deviation and explain what they measure",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "Mean, median, and mode are three different ways to answer \"what's typical here?\" "
                "The mean is the arithmetic average; the median is the middle value once sorted; "
                "the mode is whatever value shows up most. Standard deviation answers a different "
                "question: not what's typical, but how spread out the data is around that typical "
                "value."
            ),
            "technical": (
                "The mean is sensitive to outliers because every value pulls it, weighted equally; "
                "the median is a order statistic and only cares about rank, so one extreme value "
                "barely moves it. Variance is the average squared deviation from the mean "
                "(population: divide by n; sample: divide by n-1, Bessel's correction, to keep the "
                "estimator unbiased); standard deviation is variance's square root, back in the "
                "original units."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "salaries = [52000, 54000, 55000, 56000, 480000]\n\n"
                "mean = sum(salaries) / len(salaries)\n"
                "sorted_s = sorted(salaries)\n"
                "median = sorted_s[len(sorted_s) // 2]\n\n"
                "print(f\"mean:   {mean:.0f}\")\n"
                "print(f\"median: {median}\")"
            ),
            "output": "mean:   139400\nmedian: 55000",
        },
        {
            "type": "exercise",
            "prompt": "Explain in one sentence why the mean salary above (139,400) is so much higher than the median (55,000), and which one better describes a \"typical\" employee's pay.",
            "starter_code": "# One CEO earning 480,000 pulls the mean up a lot.\n# The median only looks at ____, so it barely moves.",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Reporting the mean for skewed data (income, home prices, response times) without checking the median too — a single extreme value can make the mean misleading.",
                "Confusing variance (squared units, like dollars²) with standard deviation (original units, dollars) — variance alone is rarely the number you want to report.",
                "Forgetting that a dataset can have more than one mode, or none at all, if no value repeats.",
            ],
        },
        {
            "type": "summary",
            "text": "Mean, median, and mode each answer \"what's typical\" differently. The median resists outliers; the mean doesn't. Standard deviation measures spread, in the original units.",
        },
        {
            "type": "key_terms",
            "items": ["mean", "median", "mode", "variance", "standard deviation"],
        },
    ]
}

PROBABILITY_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "State probability as a number between 0 and 1",
                "Compute the probability of independent events happening together",
                "Explain the difference between independent and conditional probability",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "Probability measures how likely something is, from 0 (never happens) to 1 "
                "(always happens). Two events are independent when one doesn't affect the other's "
                "chances — a coin flip doesn't care about the last one."
            ),
            "technical": (
                "For independent events, P(A and B) = P(A) × P(B). Conditional probability, "
                "P(A | B) — \"the probability of A given B already happened\" — is different "
                "whenever A and B aren't independent, and mixing the two up is one of the most "
                "common statistical reasoning errors (e.g. confusing P(disease | positive test) "
                "with P(positive test | disease), which are usually very different numbers)."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "p_heads = 0.5\n"
                "p_two_heads_in_a_row = p_heads * p_heads  # independent events\n\n"
                "print(p_two_heads_in_a_row)"
            ),
            "output": "0.25",
        },
        {
            "type": "exercise",
            "prompt": "A fair six-sided die is rolled twice. What's the probability of rolling a 6 both times?",
            "starter_code": "p_six = 1 / 6\np_two_sixes = ____\nprint(p_two_sixes)",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Assuming P(A | B) equals P(B | A) — these are usually different (this mix-up is called the prosecutor's fallacy in legal/medical contexts).",
                "Multiplying probabilities for events that aren't actually independent (e.g. drawing cards without replacement) — each draw changes the odds for the next.",
                "Treating a probability of 0.01 as \"basically impossible\" when it's being applied across a huge number of trials, where it becomes likely to happen at least once.",
            ],
        },
        {
            "type": "summary",
            "text": "Probability ranges from 0 to 1. Independent events multiply: P(A and B) = P(A) × P(B). Conditional probability P(A | B) is not the same as P(B | A).",
        },
        {
            "type": "key_terms",
            "items": ["probability", "independent events", "conditional probability"],
        },
    ]
}

NORMAL_DIST_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Recognize the shape and properties of a normal distribution",
                "Explain the 68-95-99.7 rule",
                "Compute a z-score and explain what it measures",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "The normal distribution is the classic bell curve — most values cluster near the "
                "average, with fewer and fewer values the further you get from it in either "
                "direction. Heights, test scores, and measurement errors often roughly follow this "
                "shape."
            ),
            "technical": (
                "A normal distribution is fully described by just two parameters: mean (μ, center) "
                "and standard deviation (σ, spread). The 68-95-99.7 rule says about 68% of values "
                "fall within 1σ of the mean, 95% within 2σ, and 99.7% within 3σ. A z-score "
                "standardizes any value as (x − μ) / σ — how many standard deviations it sits from "
                "the mean — which is what makes values from different distributions comparable."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "mean = 100\n"
                "std_dev = 15\n"
                "score = 130\n\n"
                "z = (score - mean) / std_dev\n"
                "print(f\"z-score: {z}\")"
            ),
            "output": "z-score: 2.0",
        },
        {
            "type": "exercise",
            "prompt": "A z-score of 2.0 means the score is 2 standard deviations above the mean. Using the 68-95-99.7 rule, roughly what percentage of people scored lower than this?",
            "starter_code": "# 95% of values fall within 2 std devs of the mean (from -2 to +2).\n# That leaves 5% split between both tails, 2.5% in the upper tail.\n# So roughly ____% scored below this.",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Assuming all real-world data is normally distributed — many things (income, city population, word frequency) are heavily skewed instead.",
                "Confusing a z-score with a percentage — a z-score of 2 doesn't mean \"2%\", it means \"2 standard deviations away\".",
                "Applying the 68-95-99.7 rule to a small sample and expecting it to hold exactly — it's a property of the theoretical distribution, not a guarantee for any specific small dataset.",
            ],
        },
        {
            "type": "summary",
            "text": "The normal distribution is described by its mean and standard deviation. The 68-95-99.7 rule gives quick spread estimates. A z-score standardizes a value as distance from the mean in standard deviations.",
        },
        {
            "type": "key_terms",
            "items": ["normal distribution", "68-95-99.7 rule", "z-score", "standardization"],
        },
    ]
}

MERGE_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Combine two DataFrames with pd.merge()",
                "Distinguish inner, left, right, and outer merges",
                "Predict how many rows a merge will produce",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "Real data rarely lives in one table. pd.merge() is pandas' version of a SQL JOIN "
                "— it lines up rows from two DataFrames that share a common key, like matching "
                "orders to the customers who placed them."
            ),
            "technical": (
                "`how=\"inner\"` (the default) keeps only keys present in both frames; `\"left\"` "
                "keeps every row from the left frame, filling unmatched right-side columns with "
                "NaN; `\"outer\"` keeps every key from either side. Row count after a merge isn't "
                "guaranteed to equal either input's row count — a key that repeats on both sides "
                "produces one output row per matching pair, which can silently multiply your data "
                "if you don't expect it."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "import pandas as pd\n\n"
                "orders = pd.DataFrame({\"order_id\": [1, 2, 3], \"customer_id\": [10, 11, 10]})\n"
                "customers = pd.DataFrame({\"customer_id\": [10, 11], \"name\": [\"Amara\", \"Kofi\"]})\n\n"
                "print(pd.merge(orders, customers, on=\"customer_id\", how=\"left\"))"
            ),
            "output": "   order_id  customer_id   name\n0         1           10  Amara\n1         2           11   Kofi\n2         3           10  Amara",
        },
        {
            "type": "exercise",
            "prompt": "Given the `orders` and `customers` DataFrames above, merge them so that every customer appears at least once, even one with zero orders.",
            "starter_code": "result = pd.merge(orders, customers, on=\"customer_id\", how=\"____\")\nprint(result)",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Not checking `how=` and getting an inner merge by default, which silently drops unmatched rows from both sides.",
                "Merging on a key that isn't unique on either side without realizing it — this can multiply row counts unexpectedly (a many-to-many merge).",
                "Forgetting to check for new NaN values after a left/right/outer merge, which propagate into any calculation done afterward.",
            ],
        },
        {
            "type": "summary",
            "text": "pd.merge() combines DataFrames on a shared key, like a SQL JOIN. how='inner'/'left'/'right'/'outer' controls which unmatched rows survive.",
        },
        {
            "type": "key_terms",
            "items": ["merge", "inner join", "left join", "outer join"],
        },
    ]
}

MISSING_DATA_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Detect missing values with isna()/notna()",
                "Decide between dropping and filling missing values",
                "Fill missing values with a constant, a computed value, or forward/backward fill",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "Real datasets almost always have gaps — a survey question someone skipped, a "
                "sensor reading that failed. pandas represents a missing value as NaN, and "
                "silently letting NaNs flow into a calculation is one of the most common sources "
                "of wrong analysis results."
            ),
            "technical": (
                "`df.isna()` returns a boolean mask; `df.dropna()` removes rows (or columns, with "
                "`axis=1`) containing any NaN; `df.fillna(value)` replaces them. The right choice "
                "depends on *why* data is missing — dropping is safe when missingness is random and "
                "rare, but can bias results when it isn't (e.g. higher earners skipping an income "
                "question isn't random)."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "import pandas as pd\n\n"
                "df = pd.DataFrame({\"score\": [88, None, 95, None]})\n\n"
                "print(df[\"score\"].isna().sum())\n"
                "print(df[\"score\"].fillna(df[\"score\"].mean()))"
            ),
            "output": "2\n0    88.0\n1    91.5\n2    95.0\n3    91.5\nName: score, dtype: float64",
        },
        {
            "type": "exercise",
            "prompt": "Given the `df` above, drop any row where `score` is missing instead of filling it.",
            "starter_code": "result = df.____()\nprint(result)",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Filling missing values with 0 by habit, when 0 isn't a meaningful stand-in (a missing age filled with 0 badly distorts an average).",
                "Dropping rows with any NaN using dropna() without checking how much of the dataset that discards.",
                "Computing a mean/std on a column with NaNs and assuming it silently excluded them without verifying — most pandas aggregations do skip NaN by default, but it's worth confirming for the specific method used.",
            ],
        },
        {
            "type": "summary",
            "text": "isna() finds missing values; dropna() removes them; fillna() replaces them. The right strategy depends on why the data is missing, not just what's convenient.",
        },
        {
            "type": "key_terms",
            "items": ["NaN", "isna", "dropna", "fillna"],
        },
    ]
}

GROUPBY_PANDAS_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Split a DataFrame into groups with groupby()",
                "Apply an aggregate function per group",
                "Aggregate multiple columns with different functions at once",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "groupby() is pandas' version of SQL's GROUP BY — split the data into buckets by a "
                "category, then compute something per bucket, like average score per class instead "
                "of one average for everyone."
            ),
            "technical": (
                "`df.groupby(\"col\")` returns a lazy GroupBy object; nothing is computed until you "
                "call an aggregate like `.mean()`, `.sum()`, or `.agg({...})`. `.agg()` lets you "
                "apply different functions to different columns in one pass, which is usually "
                "faster and clearer than chaining several separate groupby calls."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "import pandas as pd\n\n"
                "df = pd.DataFrame({\n"
                "    \"dept\": [\"Sales\", \"Sales\", \"Eng\", \"Eng\"],\n"
                "    \"salary\": [60000, 65000, 90000, 95000],\n"
                "})\n\n"
                "print(df.groupby(\"dept\")[\"salary\"].mean())"
            ),
            "output": "dept\nEng      92500.0\nSales    62500.0\nName: salary, dtype: float64",
        },
        {
            "type": "exercise",
            "prompt": "Given the `df` above, find the highest salary (not the average) in each department.",
            "starter_code": "result = df.groupby(\"dept\")[\"salary\"].____()\nprint(result)",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Forgetting groupby() returns nothing useful on its own — it needs an aggregate call like .mean() or .agg() to actually compute something.",
                "Grouping by a column with many unique values (like a name) when the intent was to grocery a smaller category — this produces one tiny group per row.",
                "Assuming NaN keys form their own group — by default, pandas excludes rows where the groupby key itself is NaN.",
            ],
        },
        {
            "type": "summary",
            "text": "groupby() splits data by category; an aggregate like mean() or agg() computes a value per group. Nothing is computed until the aggregate is called.",
        },
        {
            "type": "key_terms",
            "items": ["groupby", "aggregate", "split-apply-combine"],
        },
    ]
}


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        skill_names = {
            "statistics-fundamentals": "Statistics Fundamentals",
            "pandas-wrangling": "Data Wrangling with pandas",
        }
        skills: dict[str, Skill] = {}
        for slug, name in skill_names.items():
            existing = await db.execute(select(Skill).where(Skill.slug == slug))
            skill = existing.scalar_one_or_none()
            if skill is None:
                skill = Skill(name=name, slug=slug, category="statistics" if "statistics" in slug else "python")
                db.add(skill)
                await db.flush()
            skills[slug] = skill

        # ---- Statistics Fundamentals course ----
        existing_stats_course = await db.execute(select(Course).where(Course.slug == "statistics-fundamentals"))
        stats_course = existing_stats_course.scalar_one_or_none()
        if stats_course is None:
            stats_course = Course(
                title="Statistics Fundamentals",
                slug="statistics-fundamentals",
                description="The statistical foundation every data analysis question rests on: descriptive stats, probability, and the normal distribution.",
                level=LearningLevel.BEGINNER,
                estimated_hours=4,
                published=True,
            )
            db.add(stats_course)
            await db.flush()

        existing_stats_module = await db.execute(
            select(Module).where(Module.course_id == stats_course.id, Module.slug == "descriptive-and-inferential-basics")
        )
        stats_module = existing_stats_module.scalar_one_or_none()
        if stats_module is None:
            stats_module = Module(
                course_id=stats_course.id,
                title="Descriptive Statistics and Probability",
                slug="descriptive-and-inferential-basics",
                order=1,
            )
            db.add(stats_module)
            await db.flush()

        stats_lesson_specs = [
            ("mean-median-mode-and-spread", "Mean, Median, Mode, and Spread", 1, DESCRIPTIVE_STATS_CONTENT, 15, "statistics-fundamentals"),
            ("intro-to-probability", "Introduction to Probability", 2, PROBABILITY_CONTENT, 15, "statistics-fundamentals"),
            ("the-normal-distribution", "The Normal Distribution and Z-Scores", 3, NORMAL_DIST_CONTENT, 15, "statistics-fundamentals"),
        ]
        lessons: dict[str, Lesson] = {}
        for slug, title, order, content, minutes, skill_slug in stats_lesson_specs:
            existing_lesson = await db.execute(select(Lesson).where(Lesson.module_id == stats_module.id, Lesson.slug == slug))
            lesson = existing_lesson.scalar_one_or_none()
            if lesson is None:
                lesson = Lesson(
                    module_id=stats_module.id,
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

        # ---- Data Wrangling with pandas course ----
        existing_wrangle_course = await db.execute(select(Course).where(Course.slug == "data-wrangling-with-pandas"))
        wrangle_course = existing_wrangle_course.scalar_one_or_none()
        if wrangle_course is None:
            wrangle_course = Course(
                title="Data Wrangling with pandas",
                slug="data-wrangling-with-pandas",
                description="Beyond a single clean table: combining, cleaning, and summarizing real, messy data with pandas.",
                level=LearningLevel.PRACTICAL,
                estimated_hours=5,
                published=True,
            )
            db.add(wrangle_course)
            await db.flush()

        existing_wrangle_module = await db.execute(
            select(Module).where(Module.course_id == wrangle_course.id, Module.slug == "combining-and-cleaning-data")
        )
        wrangle_module = existing_wrangle_module.scalar_one_or_none()
        if wrangle_module is None:
            wrangle_module = Module(
                course_id=wrangle_course.id,
                title="Combining and Cleaning Data",
                slug="combining-and-cleaning-data",
                order=1,
            )
            db.add(wrangle_module)
            await db.flush()

        wrangle_lesson_specs = [
            ("merging-dataframes", "Merging DataFrames", 1, MERGE_CONTENT, 15, "pandas-wrangling"),
            ("handling-missing-data", "Handling Missing Data", 2, MISSING_DATA_CONTENT, 15, "pandas-wrangling"),
            ("groupby-and-aggregation", "GroupBy and Aggregation", 3, GROUPBY_PANDAS_CONTENT, 15, "pandas-wrangling"),
        ]
        for slug, title, order, content, minutes, skill_slug in wrangle_lesson_specs:
            existing_lesson = await db.execute(select(Lesson).where(Lesson.module_id == wrangle_module.id, Lesson.slug == slug))
            lesson = existing_lesson.scalar_one_or_none()
            if lesson is None:
                lesson = Lesson(
                    module_id=wrangle_module.id,
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

        # ---- Quiz on the normal distribution lesson ----
        existing_z_quiz = await db.execute(select(Quiz).where(Quiz.lesson_id == lessons["the-normal-distribution"].id))
        z_quiz = existing_z_quiz.scalar_one_or_none()
        if z_quiz is None:
            z_quiz = Quiz(lesson_id=lessons["the-normal-distribution"].id, title="Normal Distribution Check", passing_score=70)
            db.add(z_quiz)
            await db.flush()

            db.add_all(
                [
                    QuizQuestion(
                        quiz_id=z_quiz.id,
                        question_text="Roughly what percentage of values fall within 2 standard deviations of the mean in a normal distribution?",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options={"choices": ["50%", "68%", "95%", "99.7%"]},
                        correct_answer={"value": "95%"},
                        explanation="That's the '95' in the 68-95-99.7 rule.",
                        order=1,
                        points=1,
                    ),
                    QuizQuestion(
                        quiz_id=z_quiz.id,
                        question_text="A z-score of -1.5 means the value is:",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options={
                            "choices": [
                                "1.5 standard deviations below the mean",
                                "1.5% below the mean",
                                "1.5 units below zero",
                                "Impossible — z-scores can't be negative",
                            ]
                        },
                        correct_answer={"value": "1.5 standard deviations below the mean"},
                        explanation="A z-score measures distance from the mean in standard deviations; negative means below the mean.",
                        order=2,
                        points=1,
                    ),
                ]
            )

        # ---- Quiz on the groupby (pandas) lesson ----
        existing_gb2_quiz = await db.execute(select(Quiz).where(Quiz.lesson_id == lessons["groupby-and-aggregation"].id))
        gb2_quiz = existing_gb2_quiz.scalar_one_or_none()
        if gb2_quiz is None:
            gb2_quiz = Quiz(lesson_id=lessons["groupby-and-aggregation"].id, title="pandas GroupBy Check", passing_score=70)
            db.add(gb2_quiz)
            await db.flush()

            db.add_all(
                [
                    QuizQuestion(
                        quiz_id=gb2_quiz.id,
                        question_text="What does df.groupby(\"col\") return on its own, before any aggregate is called?",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options={
                            "choices": [
                                "A lazy GroupBy object — nothing is computed yet",
                                "A new DataFrame with one row per group",
                                "A single number",
                                "An error, since no aggregate was specified",
                            ]
                        },
                        correct_answer={"value": "A lazy GroupBy object — nothing is computed yet"},
                        explanation="groupby() only sets up the grouping; you need .mean(), .agg(), etc. to actually compute a result.",
                        order=1,
                        points=1,
                    ),
                    QuizQuestion(
                        quiz_id=gb2_quiz.id,
                        question_text="By default, do rows with a NaN groupby key form their own group?",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options={"choices": ["True", "False"]},
                        correct_answer={"value": "False"},
                        explanation="pandas excludes NaN keys from the grouping by default.",
                        order=2,
                        points=1,
                    ),
                ]
            )

        # ---- Add both courses to the existing Data Analytics Foundations path ----
        existing_path = await db.execute(select(LearningPath).where(LearningPath.slug == "data-analytics-foundations"))
        path = existing_path.scalar_one_or_none()
        if path is not None:
            for course, order in [(stats_course, 3), (wrangle_course, 4)]:
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
            f"({len(stats_lesson_specs)} + {len(wrangle_lesson_specs)} lessons), 2 quizzes, "
            f"added to existing learning path."
        )


if __name__ == "__main__":
    asyncio.run(seed())
