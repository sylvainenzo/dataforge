import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.assessment import QuestionType, Quiz, QuizAttempt, QuizQuestion
from app.models.career import CareerPath, CareerPathSkill, InterviewQuestion
from app.models.curriculum import Course, Lesson, Module, Skill
from app.models.datasets import Dataset
from app.models.identity import Role, User, UserRole
from app.models.knowledge_base import GlossaryTerm, Resource, Tool
from app.models.platform import AuditLog
from app.models.projects import Project, ProjectSubmission, ProjectSubmissionStatus


def slugify(text: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in text.lower()).strip("-")


async def get_stats(db: AsyncSession) -> dict:
    async def count(model, *filters) -> int:
        result = await db.execute(select(func.count()).select_from(model).where(*filters))
        return result.scalar_one()

    return {
        "user_count": await count(User),
        "course_count": await count(Course),
        "lesson_count": await count(Lesson),
        "dataset_count": await count(Dataset),
        "project_count": await count(Project),
        "quiz_attempt_count": await count(QuizAttempt),
        "code_execution_count": await count(AuditLog, AuditLog.action == "code_execution"),
    }


async def list_users(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = list(result.scalars().all())

    roles_result = await db.execute(select(UserRole.user_id, Role.name).join(Role, Role.id == UserRole.role_id))
    roles_by_user: dict[uuid.UUID, list[str]] = {}
    for user_id, role_name in roles_result.all():
        roles_by_user.setdefault(user_id, []).append(role_name)

    return [
        {
            "id": u.id,
            "email": u.email,
            "is_active": u.is_active,
            "created_at": u.created_at,
            "roles": roles_by_user.get(u.id, []),
        }
        for u in users
    ]


class RoleNotFoundError(Exception):
    pass


async def set_user_role(db: AsyncSession, *, user_id: uuid.UUID, role_name: str, grant: bool) -> None:
    role_result = await db.execute(select(Role).where(Role.name == role_name))
    role = role_result.scalar_one_or_none()
    if role is None:
        raise RoleNotFoundError(role_name)

    existing = await db.execute(
        select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role.id)
    )
    row = existing.scalar_one_or_none()

    if grant and row is None:
        db.add(UserRole(user_id=user_id, role_id=role.id))
        await db.commit()
    elif not grant and row is not None:
        await db.delete(row)
        await db.commit()


async def create_course(db: AsyncSession, *, created_by: uuid.UUID, **fields) -> Course:
    slug = fields.pop("slug", None) or slugify(fields["title"])
    course = Course(slug=slug, created_by=created_by, **fields)
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


class NotFoundError(Exception):
    pass


async def list_all_courses(db: AsyncSession) -> list[Course]:
    """Unlike curriculum_service.list_courses, this deliberately does not
    filter by published — admins need to see draft content too."""

    result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.modules)
            .selectinload(Module.lessons)
            .selectinload(Lesson.quiz)
            .selectinload(Quiz.questions)
        )
        .order_by(Course.title)
    )
    return list(result.scalars().all())


async def get_course_for_admin(db: AsyncSession, course_id: uuid.UUID) -> Course | None:
    result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.modules)
            .selectinload(Module.lessons)
            .selectinload(Lesson.quiz)
            .selectinload(Quiz.questions)
        )
        .where(Course.id == course_id)
    )
    return result.scalar_one_or_none()


async def update_course(db: AsyncSession, course_id: uuid.UUID, **fields) -> Course:
    course = await db.get(Course, course_id)
    if course is None:
        raise NotFoundError(f"Course {course_id} not found")
    for key, value in fields.items():
        if value is not None:
            setattr(course, key, value)
    await db.commit()
    await db.refresh(course)
    return course


async def delete_course(db: AsyncSession, course_id: uuid.UUID) -> None:
    course = await db.get(Course, course_id)
    if course is None:
        raise NotFoundError(f"Course {course_id} not found")
    await db.delete(course)
    await db.commit()


async def create_module(db: AsyncSession, course_id: uuid.UUID, *, title: str, slug: str | None, order: int) -> Module:
    module = Module(course_id=course_id, title=title, slug=slug or slugify(title), order=order)
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module


async def update_module(db: AsyncSession, module_id: uuid.UUID, **fields) -> Module:
    module = await db.get(Module, module_id)
    if module is None:
        raise NotFoundError(f"Module {module_id} not found")
    for key, value in fields.items():
        if value is not None:
            setattr(module, key, value)
    await db.commit()
    await db.refresh(module)
    return module


async def delete_module(db: AsyncSession, module_id: uuid.UUID) -> None:
    module = await db.get(Module, module_id)
    if module is None:
        raise NotFoundError(f"Module {module_id} not found")
    await db.delete(module)
    await db.commit()


async def create_lesson(db: AsyncSession, module_id: uuid.UUID, **fields) -> Lesson:
    slug = fields.pop("slug", None) or slugify(fields["title"])
    lesson = Lesson(module_id=module_id, slug=slug, **fields)
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return lesson


async def update_lesson(db: AsyncSession, lesson_id: uuid.UUID, **fields) -> Lesson:
    lesson = await db.get(Lesson, lesson_id)
    if lesson is None:
        raise NotFoundError(f"Lesson {lesson_id} not found")
    for key, value in fields.items():
        if value is not None:
            setattr(lesson, key, value)
    await db.commit()
    await db.refresh(lesson)
    return lesson


async def delete_lesson(db: AsyncSession, lesson_id: uuid.UUID) -> None:
    lesson = await db.get(Lesson, lesson_id)
    if lesson is None:
        raise NotFoundError(f"Lesson {lesson_id} not found")
    await db.delete(lesson)
    await db.commit()


async def create_quiz(db: AsyncSession, lesson_id: uuid.UUID, *, title: str, passing_score: int, questions: list[dict]) -> Quiz:
    quiz = Quiz(lesson_id=lesson_id, title=title, passing_score=passing_score)
    db.add(quiz)
    await db.flush()

    for q in questions:
        db.add(
            QuizQuestion(
                quiz_id=quiz.id,
                question_text=q["question_text"],
                question_type=QuestionType(q.get("question_type", "multiple_choice")),
                options=q.get("options"),
                correct_answer=q["correct_answer"],
                explanation=q.get("explanation"),
                order=q["order"],
                points=q.get("points", 1),
            )
        )

    await db.commit()
    result = await db.execute(select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == quiz.id))
    return result.scalar_one()


async def update_quiz(db: AsyncSession, quiz_id: uuid.UUID, *, title: str | None, passing_score: int | None, questions: list[dict] | None) -> Quiz:
    result = await db.execute(select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if quiz is None:
        raise NotFoundError(f"Quiz {quiz_id} not found")

    if title is not None:
        quiz.title = title
    if passing_score is not None:
        quiz.passing_score = passing_score

    if questions is not None:
        for existing_question in list(quiz.questions):
            await db.delete(existing_question)
        await db.flush()
        for q in questions:
            db.add(
                QuizQuestion(
                    quiz_id=quiz.id,
                    question_text=q["question_text"],
                    question_type=QuestionType(q.get("question_type", "multiple_choice")),
                    options=q.get("options"),
                    correct_answer=q["correct_answer"],
                    explanation=q.get("explanation"),
                    order=q["order"],
                    points=q.get("points", 1),
                )
            )

    await db.commit()
    result = await db.execute(select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == quiz_id))
    return result.scalar_one()


async def delete_quiz(db: AsyncSession, quiz_id: uuid.UUID) -> None:
    quiz = await db.get(Quiz, quiz_id)
    if quiz is None:
        raise NotFoundError(f"Quiz {quiz_id} not found")
    await db.delete(quiz)
    await db.commit()


# ---- Resources & Glossary ----


async def list_all_resources(db: AsyncSession) -> list[Resource]:
    result = await db.execute(select(Resource).order_by(Resource.title))
    return list(result.scalars().all())


async def create_resource(db: AsyncSession, **fields) -> Resource:
    resource = Resource(**fields)
    db.add(resource)
    await db.commit()
    await db.refresh(resource)
    return resource


async def update_resource(db: AsyncSession, resource_id: uuid.UUID, **fields) -> Resource:
    resource = await db.get(Resource, resource_id)
    if resource is None:
        raise NotFoundError(f"Resource {resource_id} not found")
    for key, value in fields.items():
        if value is not None:
            setattr(resource, key, value)
    await db.commit()
    await db.refresh(resource)
    return resource


async def delete_resource(db: AsyncSession, resource_id: uuid.UUID) -> None:
    resource = await db.get(Resource, resource_id)
    if resource is None:
        raise NotFoundError(f"Resource {resource_id} not found")
    await db.delete(resource)
    await db.commit()


async def list_all_glossary_terms(db: AsyncSession) -> list[GlossaryTerm]:
    result = await db.execute(select(GlossaryTerm).order_by(GlossaryTerm.term))
    return list(result.scalars().all())


async def create_glossary_term(db: AsyncSession, *, term: str, slug: str | None, **fields) -> GlossaryTerm:
    glossary_term = GlossaryTerm(term=term, slug=slug or slugify(term), **fields)
    db.add(glossary_term)
    await db.commit()
    await db.refresh(glossary_term)
    return glossary_term


async def update_glossary_term(db: AsyncSession, term_id: uuid.UUID, **fields) -> GlossaryTerm:
    glossary_term = await db.get(GlossaryTerm, term_id)
    if glossary_term is None:
        raise NotFoundError(f"Glossary term {term_id} not found")
    for key, value in fields.items():
        if value is not None:
            setattr(glossary_term, key, value)
    await db.commit()
    await db.refresh(glossary_term)
    return glossary_term


async def delete_glossary_term(db: AsyncSession, term_id: uuid.UUID) -> None:
    glossary_term = await db.get(GlossaryTerm, term_id)
    if glossary_term is None:
        raise NotFoundError(f"Glossary term {term_id} not found")
    await db.delete(glossary_term)
    await db.commit()


# ---- Tools ----


async def list_all_tools(db: AsyncSession) -> list[Tool]:
    result = await db.execute(select(Tool).order_by(Tool.name))
    return list(result.scalars().all())


async def create_tool(db: AsyncSession, *, name: str, slug: str | None, **fields) -> Tool:
    tool = Tool(name=name, slug=slug or slugify(name), **fields)
    db.add(tool)
    await db.commit()
    await db.refresh(tool)
    return tool


async def update_tool(db: AsyncSession, tool_id: uuid.UUID, **fields) -> Tool:
    tool = await db.get(Tool, tool_id)
    if tool is None:
        raise NotFoundError(f"Tool {tool_id} not found")
    for key, value in fields.items():
        if value is not None:
            setattr(tool, key, value)
    await db.commit()
    await db.refresh(tool)
    return tool


async def delete_tool(db: AsyncSession, tool_id: uuid.UUID) -> None:
    tool = await db.get(Tool, tool_id)
    if tool is None:
        raise NotFoundError(f"Tool {tool_id} not found")
    await db.delete(tool)
    await db.commit()


# ---- Career paths ----


async def _career_path_skill_weights(db: AsyncSession, career_path_id: uuid.UUID) -> dict[str, float]:
    result = await db.execute(
        select(Skill.slug, CareerPathSkill.weight)
        .join(CareerPathSkill, CareerPathSkill.skill_id == Skill.id)
        .where(CareerPathSkill.career_path_id == career_path_id)
    )
    return {slug: float(weight) for slug, weight in result.all()}


async def _set_career_path_skill_weights(db: AsyncSession, career_path_id: uuid.UUID, skill_weights: dict[str, float]) -> None:
    existing = await db.execute(select(CareerPathSkill).where(CareerPathSkill.career_path_id == career_path_id))
    for row in existing.scalars().all():
        await db.delete(row)
    await db.flush()

    for skill_slug, weight in skill_weights.items():
        skill_result = await db.execute(select(Skill).where(Skill.slug == skill_slug))
        skill = skill_result.scalar_one_or_none()
        if skill is None:
            continue
        db.add(CareerPathSkill(career_path_id=career_path_id, skill_id=skill.id, weight=weight))


async def list_all_career_paths(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(CareerPath).order_by(CareerPath.name))
    paths = list(result.scalars().all())
    return [
        {
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "description": p.description,
            "skill_weights": await _career_path_skill_weights(db, p.id),
        }
        for p in paths
    ]


async def create_career_path(db: AsyncSession, *, name: str, slug: str | None, description: str | None, skill_weights: dict[str, float]) -> dict:
    career_path = CareerPath(name=name, slug=slug or slugify(name), description=description)
    db.add(career_path)
    await db.flush()
    await _set_career_path_skill_weights(db, career_path.id, skill_weights)
    await db.commit()
    return {
        "id": career_path.id,
        "name": career_path.name,
        "slug": career_path.slug,
        "description": career_path.description,
        "skill_weights": skill_weights,
    }


async def update_career_path(db: AsyncSession, career_path_id: uuid.UUID, **fields) -> dict:
    career_path = await db.get(CareerPath, career_path_id)
    if career_path is None:
        raise NotFoundError(f"Career path {career_path_id} not found")

    skill_weights = fields.pop("skill_weights", None)
    for key, value in fields.items():
        if value is not None:
            setattr(career_path, key, value)
    if skill_weights is not None:
        await _set_career_path_skill_weights(db, career_path_id, skill_weights)

    await db.commit()
    return {
        "id": career_path.id,
        "name": career_path.name,
        "slug": career_path.slug,
        "description": career_path.description,
        "skill_weights": skill_weights if skill_weights is not None else await _career_path_skill_weights(db, career_path_id),
    }


async def delete_career_path(db: AsyncSession, career_path_id: uuid.UUID) -> None:
    career_path = await db.get(CareerPath, career_path_id)
    if career_path is None:
        raise NotFoundError(f"Career path {career_path_id} not found")
    await db.delete(career_path)
    await db.commit()


# ---- Interview questions ----


async def list_all_interview_questions(db: AsyncSession) -> list[InterviewQuestion]:
    result = await db.execute(
        select(InterviewQuestion).order_by(InterviewQuestion.category, InterviewQuestion.difficulty)
    )
    return list(result.scalars().all())


async def create_interview_question(db: AsyncSession, **fields) -> InterviewQuestion:
    question = InterviewQuestion(**fields)
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


async def update_interview_question(db: AsyncSession, question_id: uuid.UUID, **fields) -> InterviewQuestion:
    question = await db.get(InterviewQuestion, question_id)
    if question is None:
        raise NotFoundError(f"Interview question {question_id} not found")
    for key, value in fields.items():
        if value is not None:
            setattr(question, key, value)
    await db.commit()
    await db.refresh(question)
    return question


async def delete_interview_question(db: AsyncSession, question_id: uuid.UUID) -> None:
    question = await db.get(InterviewQuestion, question_id)
    if question is None:
        raise NotFoundError(f"Interview question {question_id} not found")
    await db.delete(question)
    await db.commit()


# ---- Projects ----


async def list_all_projects(db: AsyncSession) -> list[Project]:
    result = await db.execute(select(Project).order_by(Project.title))
    return list(result.scalars().all())


async def create_project(db: AsyncSession, *, title: str, slug: str | None, **fields) -> Project:
    project = Project(title=title, slug=slug or slugify(title), **fields)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def update_project(db: AsyncSession, project_id: uuid.UUID, **fields) -> Project:
    project = await db.get(Project, project_id)
    if project is None:
        raise NotFoundError(f"Project {project_id} not found")
    for key, value in fields.items():
        if value is not None:
            setattr(project, key, value)
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project_id: uuid.UUID) -> None:
    project = await db.get(Project, project_id)
    if project is None:
        raise NotFoundError(f"Project {project_id} not found")
    await db.delete(project)
    await db.commit()


# ---- Project submission review queue ----


async def list_all_submissions(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(ProjectSubmission, Project.title, User.email)
        .join(Project, Project.id == ProjectSubmission.project_id)
        .join(User, User.id == ProjectSubmission.user_id)
        .order_by(ProjectSubmission.submitted_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": sub.id,
            "project_id": sub.project_id,
            "project_title": project_title,
            "user_id": sub.user_id,
            "user_email": user_email,
            "submission_url": sub.submission_url,
            "status": sub.status.value,
            "feedback": sub.feedback,
            "submitted_at": sub.submitted_at,
            "reviewed_at": sub.reviewed_at,
        }
        for sub, project_title, user_email in rows
    ]


async def review_submission(db: AsyncSession, submission_id: uuid.UUID, *, status: str, feedback: str | None) -> dict:
    submission = await db.get(ProjectSubmission, submission_id)
    if submission is None:
        raise NotFoundError(f"Submission {submission_id} not found")

    submission.status = ProjectSubmissionStatus(status)
    submission.feedback = feedback
    submission.reviewed_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(submission)

    project = await db.get(Project, submission.project_id)
    user = await db.get(User, submission.user_id)
    return {
        "id": submission.id,
        "project_id": submission.project_id,
        "project_title": project.title if project else "",
        "user_id": submission.user_id,
        "user_email": user.email if user else "",
        "submission_url": submission.submission_url,
        "status": submission.status.value,
        "feedback": submission.feedback,
        "submitted_at": submission.submitted_at,
        "reviewed_at": submission.reviewed_at,
    }


# ---- Datasets (metadata only — creating a new dataset requires a real
# uploaded file, handled by the existing user-upload ingest path, not
# admin CRUD) ----


async def list_all_datasets(db: AsyncSession) -> list[Dataset]:
    result = await db.execute(select(Dataset).order_by(Dataset.name))
    return list(result.scalars().all())


async def update_dataset(db: AsyncSession, dataset_id: uuid.UUID, **fields) -> Dataset:
    dataset = await db.get(Dataset, dataset_id)
    if dataset is None:
        raise NotFoundError(f"Dataset {dataset_id} not found")
    for key, value in fields.items():
        if value is not None:
            setattr(dataset, key, value)
    await db.commit()
    await db.refresh(dataset)
    return dataset


async def delete_dataset(db: AsyncSession, dataset_id: uuid.UUID) -> None:
    dataset = await db.get(Dataset, dataset_id)
    if dataset is None:
        raise NotFoundError(f"Dataset {dataset_id} not found")
    await db.delete(dataset)
    await db.commit()
