"""Idempotent curriculum seed — "Data Visualization Fundamentals" (3
lessons), pairing with the Data Visualization Lab (real matplotlib/seaborn
execution, added this session). Added to the existing "Data Analytics
Foundations" learning path.

Run: python3 scripts/seed_curriculum_dataviz.py
(Run seed_curriculum.py first — this reuses its learning path.)
"""

import asyncio

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.base import LearningLevel
from app.models.curriculum import Course, LearningPath, LearningPathCourse, Lesson, LessonSkill, Module, Skill

CHART_SELECTION_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Match a common analysis question to the right chart type",
                "Explain when a bar chart is more honest than a line chart, and vice versa",
                "Identify a chart that misleads by omission or distortion",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "The right chart depends on the question, not on what looks impressive. \"How did X change over "
                "time?\" wants a line chart. \"How do these categories compare?\" wants a bar chart. \"Is there "
                "a relationship between two numbers?\" wants a scatter plot. Picking the wrong shape for the "
                "question is one of the most common ways a chart quietly misleads."
            ),
            "technical": (
                "A line chart implies continuity between points — it's appropriate for a genuinely continuous "
                "sequence like time, and misleading for unordered categories (a line connecting \"Sales in "
                "France\" to \"Sales in Japan\" implies a trend between them that doesn't exist). A bar chart's "
                "y-axis should almost always start at zero, since bar length is read as proportional to value; "
                "a truncated y-axis on a bar chart exaggerates small differences — the single most common "
                "chart-honesty violation."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "import matplotlib.pyplot as plt\n\n"
                "months = [\"Jan\", \"Feb\", \"Mar\", \"Apr\"]\n"
                "revenue = [12000, 12400, 12100, 15800]\n\n"
                "plt.figure(figsize=(6, 4))\n"
                "plt.plot(months, revenue, marker=\"o\")\n"
                "plt.title(\"Revenue Over Time\")\n"
                "plt.ylim(0, max(revenue) * 1.1)  # start the axis at 0 — don't exaggerate the trend\n"
                "plt.savefig(\"chart.png\")"
            ),
            "output": None,
        },
        {
            "type": "exercise",
            "prompt": "In the Data Visualization Lab, plot `revenue` as a bar chart instead, and compare how it reads versus the line chart above.",
            "starter_code": "plt.bar(months, revenue)\nplt.title(\"Revenue by Month\")\nplt.savefig(\"chart.png\")",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Truncating a bar chart's y-axis to start above zero, which visually exaggerates small differences between bars.",
                "Using a line chart to connect unordered categories, implying a trend or continuity that doesn't exist between them.",
                "Using a pie chart for more than about five categories, or for values that don't sum to a meaningful whole — differences between similar slice sizes are hard to judge by eye.",
            ],
        },
        {
            "type": "summary",
            "text": "Pick the chart type based on the question: trend over time → line, compare categories → bar, relationship between two numbers → scatter. Bar chart axes should start at zero.",
        },
        {
            "type": "key_terms",
            "items": ["line chart", "bar chart", "scatter plot", "truncated axis"],
        },
    ]
}

MATPLOTLIB_BASICS_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Create a figure and plot data with matplotlib's pyplot interface",
                "Add a title, axis labels, and a legend to a chart",
                "Save a chart to a file instead of displaying it interactively",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "matplotlib is Python's foundational plotting library — most other Python charting tools "
                "(including seaborn) are built on top of it. The `pyplot` interface (usually imported as `plt`) "
                "gives you a simple, step-by-step way to build a chart: create it, add data, label it, save it."
            ),
            "technical": (
                "`plt.figure(figsize=(w, h))` sets the canvas size in inches; each `plt.plot()`/`plt.bar()`/etc. "
                "call adds a layer to the current axes. In a script or server environment with no display "
                "(like this Lab's sandbox), `plt.savefig(path)` writes the figure to a file instead of opening "
                "an interactive window — the Lab picks up any `.png` file your script saves and renders it."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "import matplotlib.pyplot as plt\n\n"
                "study_hours = [1, 2, 3, 4, 5]\n"
                "exam_scores = [52, 61, 68, 79, 88]\n\n"
                "plt.figure(figsize=(6, 4))\n"
                "plt.plot(study_hours, exam_scores, marker=\"o\", label=\"Score\")\n"
                "plt.title(\"Study Hours vs. Exam Score\")\n"
                "plt.xlabel(\"Study hours\")\n"
                "plt.ylabel(\"Exam score\")\n"
                "plt.legend()\n"
                "plt.savefig(\"chart.png\")"
            ),
            "output": None,
        },
        {
            "type": "exercise",
            "prompt": "In the Data Visualization Lab, add a second line to the chart above for a different student's scores, and give it its own label.",
            "starter_code": "plt.plot(study_hours, exam_scores, marker=\"o\", label=\"Student A\")\nplt.plot(study_hours, ____, marker=\"o\", label=\"Student B\")\nplt.legend()\nplt.savefig(\"chart.png\")",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Forgetting `plt.savefig()` — without it, a script running headlessly produces no visible output at all.",
                "Calling `plt.plot()` many times across a notebook without a new `plt.figure()`, which silently draws everything onto the same chart.",
                "Skipping axis labels and a title — a chart without labels forces the reader to guess what they're looking at.",
            ],
        },
        {
            "type": "summary",
            "text": "matplotlib's pyplot interface builds a chart step by step: figure, plot data, label axes, save. plt.savefig() is how a script without a display produces a chart file.",
        },
        {
            "type": "key_terms",
            "items": ["matplotlib", "pyplot", "figure", "savefig"],
        },
    ]
}

SEABORN_CONTENT = {
    "blocks": [
        {
            "type": "objectives",
            "items": [
                "Explain what seaborn adds on top of matplotlib",
                "Create a bar plot directly from a pandas DataFrame with seaborn",
                "Use a box plot to show a distribution's spread and outliers at a glance",
            ],
        },
        {
            "type": "explanation",
            "beginner": (
                "seaborn is built on matplotlib but works directly with DataFrames and handles a lot of "
                "styling automatically — grouping, coloring by category, and sensible defaults that would take "
                "several lines of raw matplotlib to reproduce."
            ),
            "technical": (
                "seaborn functions typically take `data=`, `x=`, and `y=` as column names rather than raw "
                "arrays, and return a matplotlib `Axes` object — so `plt.savefig()` still works exactly the "
                "same way afterward, since seaborn draws onto the same current figure. A box plot's box shows "
                "the interquartile range (25th–75th percentile), the line inside is the median, and points "
                "beyond the whiskers are flagged as outliers by a fixed rule (1.5× the IQR), not manually "
                "chosen."
            ),
        },
        {
            "type": "code",
            "language": "python",
            "code": (
                "import matplotlib.pyplot as plt\n"
                "import seaborn as sns\n"
                "import pandas as pd\n\n"
                "df = pd.DataFrame({\n"
                "    \"department\": [\"Sales\", \"Sales\", \"Eng\", \"Eng\", \"Eng\"],\n"
                "    \"salary\": [60000, 65000, 90000, 95000, 120000],\n"
                "})\n\n"
                "plt.figure(figsize=(6, 4))\n"
                "sns.boxplot(data=df, x=\"department\", y=\"salary\")\n"
                "plt.title(\"Salary Distribution by Department\")\n"
                "plt.savefig(\"chart.png\")"
            ),
            "output": None,
        },
        {
            "type": "exercise",
            "prompt": "In the Data Visualization Lab, use sns.barplot instead of sns.boxplot on the same DataFrame to show the average salary per department.",
            "starter_code": "sns.barplot(data=df, x=\"department\", y=\"salary\")\nplt.title(\"Average Salary by Department\")\nplt.savefig(\"chart.png\")",
        },
        {
            "type": "common_mistakes",
            "items": [
                "Forgetting `import matplotlib.pyplot as plt` alongside seaborn — you still need plt.savefig() to output the chart, seaborn doesn't replace that.",
                "Using a bar chart (which shows a mean) when a box plot (which shows the full spread) would reveal that two groups with similar averages have very different variability.",
                "Not sorting or ordering categories intentionally — seaborn's default category order is whatever order they first appear in the data, which may not be the most readable order.",
            ],
        },
        {
            "type": "summary",
            "text": "seaborn works directly with DataFrame columns and handles grouping/styling automatically. A box plot shows spread and outliers; a bar plot alone only shows the average.",
        },
        {
            "type": "key_terms",
            "items": ["seaborn", "box plot", "interquartile range", "outlier"],
        },
    ]
}


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        existing_skill = await db.execute(select(Skill).where(Skill.slug == "data-visualization"))
        skill = existing_skill.scalar_one_or_none()
        if skill is None:
            skill = Skill(name="Data Visualization", slug="data-visualization", category="python")
            db.add(skill)
            await db.flush()

        existing_course = await db.execute(select(Course).where(Course.slug == "data-visualization-fundamentals"))
        course = existing_course.scalar_one_or_none()
        if course is None:
            course = Course(
                title="Data Visualization Fundamentals",
                slug="data-visualization-fundamentals",
                description="Choosing the right chart, and building it for real with matplotlib and seaborn in the Data Visualization Lab.",
                level=LearningLevel.PRACTICAL,
                estimated_hours=3,
                published=True,
            )
            db.add(course)
            await db.flush()

        existing_module = await db.execute(
            select(Module).where(Module.course_id == course.id, Module.slug == "charts-that-work")
        )
        module = existing_module.scalar_one_or_none()
        if module is None:
            module = Module(course_id=course.id, title="Charts That Work", slug="charts-that-work", order=1)
            db.add(module)
            await db.flush()

        lesson_specs = [
            ("choosing-the-right-chart", "Choosing the Right Chart", 1, CHART_SELECTION_CONTENT, 15),
            ("matplotlib-basics", "Matplotlib Basics", 2, MATPLOTLIB_BASICS_CONTENT, 15),
            ("seaborn-for-statistical-plots", "Seaborn for Statistical Plots", 3, SEABORN_CONTENT, 15),
        ]
        for slug, title, order, content, minutes in lesson_specs:
            existing_lesson = await db.execute(select(Lesson).where(Lesson.module_id == module.id, Lesson.slug == slug))
            lesson = existing_lesson.scalar_one_or_none()
            if lesson is None:
                lesson = Lesson(
                    module_id=module.id, title=title, slug=slug, order=order,
                    content=content, estimated_minutes=minutes, published=True,
                )
                db.add(lesson)
                await db.flush()

                existing_link = await db.execute(
                    select(LessonSkill).where(LessonSkill.lesson_id == lesson.id, LessonSkill.skill_id == skill.id)
                )
                if existing_link.scalar_one_or_none() is None:
                    db.add(LessonSkill(lesson_id=lesson.id, skill_id=skill.id))
            else:
                lesson.order = order

        existing_path = await db.execute(select(LearningPath).where(LearningPath.slug == "data-analytics-foundations"))
        path = existing_path.scalar_one_or_none()
        if path is not None:
            existing_lpc = await db.execute(
                select(LearningPathCourse).where(
                    LearningPathCourse.learning_path_id == path.id, LearningPathCourse.course_id == course.id
                )
            )
            if existing_lpc.scalar_one_or_none() is None:
                db.add(LearningPathCourse(learning_path_id=path.id, course_id=course.id, order=8))

        await db.commit()
        print(f"Seed complete: 1 skill, 1 course ({len(lesson_specs)} lessons), added to learning path.")


if __name__ == "__main__":
    asyncio.run(seed())
