import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_current_user
from app.core.db import get_db
from app.models.learning_science import ProgressStatus
from app.schemas.curriculum import (
    CourseDetail,
    CourseSummary,
    LearningPathDetail,
    LearningPathSummary,
    LessonDetail,
    QuizAttemptResult,
    QuizAttemptSubmit,
    QuizDetail,
)
from app.services import curriculum_service

router = APIRouter(tags=["curriculum"])


@router.get("/learning-paths", response_model=list[LearningPathSummary])
async def list_learning_paths(db: AsyncSession = Depends(get_db)):
    return await curriculum_service.list_learning_paths(db)


@router.get("/learning-paths/{slug}", response_model=LearningPathDetail)
async def get_learning_path(slug: str, db: AsyncSession = Depends(get_db)):
    path = await curriculum_service.get_learning_path(db, slug)
    if path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning path not found")
    return LearningPathDetail(
        id=path.id,
        title=path.title,
        slug=path.slug,
        description=path.description,
        courses=[
            CourseSummary.model_validate(lpc.course)
            for lpc in sorted(path.courses, key=lambda x: x.order)
        ],
    )


@router.get("/courses", response_model=list[CourseSummary])
async def list_courses(db: AsyncSession = Depends(get_db)):
    return await curriculum_service.list_courses(db)


@router.get("/courses/{slug}", response_model=CourseDetail)
async def get_course(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    course = await curriculum_service.get_course_detail(db, slug)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    course.modules.sort(key=lambda m: m.order)
    lesson_ids = []
    for module in course.modules:
        module.lessons.sort(key=lambda lesson: lesson.order)
        lesson_ids.extend(lesson.id for lesson in module.lessons)
    completed_lesson_ids = await curriculum_service.get_completed_lesson_ids(
        db, user_id=current_user.id, lesson_ids=lesson_ids
    )
    detail = CourseDetail.model_validate(course)
    detail.completed_lesson_ids = completed_lesson_ids
    return detail


@router.get("/lessons/{slug}", response_model=LessonDetail)
async def get_lesson(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    lesson = await curriculum_service.get_lesson_detail(db, slug)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    skills = await curriculum_service.get_lesson_skills(db, lesson.id)
    quiz = await curriculum_service.get_quiz_for_lesson(db, lesson.id)
    await curriculum_service.mark_lesson_progress(
        db, user_id=current_user.id, lesson_id=lesson.id, status=ProgressStatus.IN_PROGRESS
    )
    return LessonDetail(
        id=lesson.id,
        title=lesson.title,
        slug=lesson.slug,
        order=lesson.order,
        content=lesson.content,
        estimated_minutes=lesson.estimated_minutes,
        skills=skills,
        quiz_id=quiz.id if quiz else None,
    )


@router.post("/lessons/{slug}/complete", status_code=status.HTTP_204_NO_CONTENT)
async def complete_lesson(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    lesson = await curriculum_service.get_lesson_detail(db, slug)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    await curriculum_service.mark_lesson_progress(
        db, user_id=current_user.id, lesson_id=lesson.id, status=ProgressStatus.COMPLETED
    )


@router.get("/quizzes/{quiz_id}", response_model=QuizDetail)
async def get_quiz(
    quiz_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    quiz = await curriculum_service.get_quiz_detail(db, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    quiz.questions.sort(key=lambda q: q.order)
    return quiz


@router.post("/quizzes/{quiz_id}/attempts", response_model=QuizAttemptResult)
async def submit_quiz(
    quiz_id: uuid.UUID,
    body: QuizAttemptSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    quiz = await curriculum_service.get_quiz_detail(db, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    score, passed, correct_count = await curriculum_service.submit_quiz_attempt(
        db, user_id=current_user.id, quiz=quiz, answers=body.answers
    )
    return QuizAttemptResult(
        score=score, passed=passed, correct_count=correct_count, total_questions=len(quiz.questions)
    )
