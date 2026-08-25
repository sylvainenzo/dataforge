import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, require_role
from app.core.db import get_db
from app.schemas.admin import (
    AdminCareerPathCreate,
    AdminCareerPathRead,
    AdminCareerPathUpdate,
    AdminCourseCreate,
    AdminCourseRead,
    AdminCourseUpdate,
    AdminDatasetRead,
    AdminDatasetUpdate,
    AdminGlossaryTermCreate,
    AdminGlossaryTermUpdate,
    AdminInterviewQuestionCreate,
    AdminInterviewQuestionRead,
    AdminInterviewQuestionUpdate,
    AdminLessonCreate,
    AdminLessonRead,
    AdminLessonUpdate,
    AdminModuleCreate,
    AdminModuleRead,
    AdminModuleUpdate,
    AdminProjectCreate,
    AdminProjectRead,
    AdminProjectSubmissionRead,
    AdminProjectSubmissionReview,
    AdminProjectUpdate,
    AdminQuizCreate,
    AdminQuizRead,
    AdminQuizUpdate,
    AdminResourceCreate,
    AdminResourceUpdate,
    AdminStats,
    AdminToolCreate,
    AdminToolRead,
    AdminToolUpdate,
    AdminUserRead,
    SetUserRoleRequest,
)
from app.schemas.curriculum import CourseSummary
from app.schemas.knowledge_base import GlossaryTermRead, ResourceRead
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["admin"])

require_admin = require_role("admin")


@router.get("/stats", response_model=AdminStats)
async def get_stats(db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)):
    return await admin_service.get_stats(db)


@router.get("/users", response_model=list[AdminUserRead])
async def list_users(db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)):
    return await admin_service.list_users(db)


@router.patch("/users/{user_id}/role", status_code=status.HTTP_204_NO_CONTENT)
async def set_user_role(
    user_id: uuid.UUID,
    body: SetUserRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_admin),
):
    if user_id == current_user.id and body.role == "admin" and not body.grant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot remove your own admin role")

    try:
        await admin_service.set_user_role(db, user_id=user_id, role_name=body.role, grant=body.grant)
    except admin_service.RoleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Role '{body.role}' does not exist"
        ) from exc


@router.get("/courses", response_model=list[AdminCourseRead])
async def list_admin_courses(db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)):
    return await admin_service.list_all_courses(db)


@router.post("/courses", response_model=CourseSummary, status_code=status.HTTP_201_CREATED)
async def create_course(
    body: AdminCourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_admin),
):
    course = await admin_service.create_course(db, created_by=current_user.id, **body.model_dump())
    return course


@router.get("/courses/{course_id}", response_model=AdminCourseRead)
async def get_admin_course(
    course_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    course = await admin_service.get_course_for_admin(db, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.patch("/courses/{course_id}", response_model=AdminCourseRead)
async def update_course(
    course_id: uuid.UUID,
    body: AdminCourseUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    try:
        await admin_service.update_course(db, course_id, **body.model_dump())
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found") from exc
    return await admin_service.get_course_for_admin(db, course_id)


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    try:
        await admin_service.delete_course(db, course_id)
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found") from exc


@router.post("/courses/{course_id}/modules", response_model=AdminModuleRead, status_code=status.HTTP_201_CREATED)
async def create_module(
    course_id: uuid.UUID,
    body: AdminModuleCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    return await admin_service.create_module(db, course_id, **body.model_dump())


@router.patch("/modules/{module_id}", response_model=AdminModuleRead)
async def update_module(
    module_id: uuid.UUID,
    body: AdminModuleUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    try:
        return await admin_service.update_module(db, module_id, **body.model_dump())
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found") from exc


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    try:
        await admin_service.delete_module(db, module_id)
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found") from exc


@router.post("/modules/{module_id}/lessons", response_model=AdminLessonRead, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    module_id: uuid.UUID,
    body: AdminLessonCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    return await admin_service.create_lesson(db, module_id, **body.model_dump())


@router.patch("/lessons/{lesson_id}", response_model=AdminLessonRead)
async def update_lesson(
    lesson_id: uuid.UUID,
    body: AdminLessonUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    try:
        return await admin_service.update_lesson(db, lesson_id, **body.model_dump())
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found") from exc


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    try:
        await admin_service.delete_lesson(db, lesson_id)
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found") from exc


@router.post("/lessons/{lesson_id}/quiz", response_model=AdminQuizRead, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    lesson_id: uuid.UUID,
    body: AdminQuizCreate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    return await admin_service.create_quiz(
        db, lesson_id, title=body.title, passing_score=body.passing_score,
        questions=[q.model_dump() for q in body.questions],
    )


@router.patch("/quizzes/{quiz_id}", response_model=AdminQuizRead)
async def update_quiz(
    quiz_id: uuid.UUID,
    body: AdminQuizUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    try:
        return await admin_service.update_quiz(
            db, quiz_id, title=body.title, passing_score=body.passing_score,
            questions=[q.model_dump() for q in body.questions] if body.questions is not None else None,
        )
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found") from exc


@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz(
    quiz_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    try:
        await admin_service.delete_quiz(db, quiz_id)
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found") from exc


# ---- Resources & Glossary ----


@router.get("/resources", response_model=list[ResourceRead])
async def list_admin_resources(db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)):
    return await admin_service.list_all_resources(db)


@router.post("/resources", response_model=ResourceRead, status_code=status.HTTP_201_CREATED)
async def create_resource(
    body: AdminResourceCreate, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    return await admin_service.create_resource(db, **body.model_dump())


@router.patch("/resources/{resource_id}", response_model=ResourceRead)
async def update_resource(
    resource_id: uuid.UUID,
    body: AdminResourceUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    try:
        return await admin_service.update_resource(db, resource_id, **body.model_dump())
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found") from exc


@router.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    try:
        await admin_service.delete_resource(db, resource_id)
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found") from exc


@router.get("/glossary", response_model=list[GlossaryTermRead])
async def list_admin_glossary_terms(db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)):
    return await admin_service.list_all_glossary_terms(db)


@router.post("/glossary", response_model=GlossaryTermRead, status_code=status.HTTP_201_CREATED)
async def create_glossary_term(
    body: AdminGlossaryTermCreate, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    return await admin_service.create_glossary_term(db, **body.model_dump())


@router.patch("/glossary/{term_id}", response_model=GlossaryTermRead)
async def update_glossary_term(
    term_id: uuid.UUID,
    body: AdminGlossaryTermUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    try:
        return await admin_service.update_glossary_term(db, term_id, **body.model_dump())
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Glossary term not found") from exc


@router.delete("/glossary/{term_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_glossary_term(
    term_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    try:
        await admin_service.delete_glossary_term(db, term_id)
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Glossary term not found") from exc


# ---- Tools ----


@router.get("/tools", response_model=list[AdminToolRead])
async def list_admin_tools(db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)):
    return await admin_service.list_all_tools(db)


@router.post("/tools", response_model=AdminToolRead, status_code=status.HTTP_201_CREATED)
async def create_tool(
    body: AdminToolCreate, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    return await admin_service.create_tool(db, **body.model_dump())


@router.patch("/tools/{tool_id}", response_model=AdminToolRead)
async def update_tool(
    tool_id: uuid.UUID,
    body: AdminToolUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    try:
        return await admin_service.update_tool(db, tool_id, **body.model_dump())
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found") from exc


@router.delete("/tools/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    try:
        await admin_service.delete_tool(db, tool_id)
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found") from exc


# ---- Career paths ----


@router.get("/career-paths", response_model=list[AdminCareerPathRead])
async def list_admin_career_paths(db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)):
    return await admin_service.list_all_career_paths(db)


@router.post("/career-paths", response_model=AdminCareerPathRead, status_code=status.HTTP_201_CREATED)
async def create_career_path(
    body: AdminCareerPathCreate, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    return await admin_service.create_career_path(db, **body.model_dump())


@router.patch("/career-paths/{career_path_id}", response_model=AdminCareerPathRead)
async def update_career_path(
    career_path_id: uuid.UUID,
    body: AdminCareerPathUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    try:
        return await admin_service.update_career_path(db, career_path_id, **body.model_dump())
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Career path not found") from exc


@router.delete("/career-paths/{career_path_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_career_path(
    career_path_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    try:
        await admin_service.delete_career_path(db, career_path_id)
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Career path not found") from exc


# ---- Interview questions ----


@router.get("/interview-questions", response_model=list[AdminInterviewQuestionRead])
async def list_admin_interview_questions(db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)):
    return await admin_service.list_all_interview_questions(db)


@router.post("/interview-questions", response_model=AdminInterviewQuestionRead, status_code=status.HTTP_201_CREATED)
async def create_interview_question(
    body: AdminInterviewQuestionCreate, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    return await admin_service.create_interview_question(db, **body.model_dump())


@router.patch("/interview-questions/{question_id}", response_model=AdminInterviewQuestionRead)
async def update_interview_question(
    question_id: uuid.UUID,
    body: AdminInterviewQuestionUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    try:
        return await admin_service.update_interview_question(db, question_id, **body.model_dump())
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview question not found") from exc


@router.delete("/interview-questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview_question(
    question_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    try:
        await admin_service.delete_interview_question(db, question_id)
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview question not found") from exc


# ---- Projects ----


@router.get("/projects", response_model=list[AdminProjectRead])
async def list_admin_projects(db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)):
    return await admin_service.list_all_projects(db)


@router.post("/projects", response_model=AdminProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: AdminProjectCreate, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    return await admin_service.create_project(db, **body.model_dump())


@router.patch("/projects/{project_id}", response_model=AdminProjectRead)
async def update_project(
    project_id: uuid.UUID,
    body: AdminProjectUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    try:
        return await admin_service.update_project(db, project_id, **body.model_dump())
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from exc


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    try:
        await admin_service.delete_project(db, project_id)
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from exc


# ---- Project submission review queue ----


@router.get("/project-submissions", response_model=list[AdminProjectSubmissionRead])
async def list_admin_submissions(db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)):
    return await admin_service.list_all_submissions(db)


@router.patch("/project-submissions/{submission_id}", response_model=AdminProjectSubmissionRead)
async def review_submission(
    submission_id: uuid.UUID,
    body: AdminProjectSubmissionReview,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    try:
        return await admin_service.review_submission(
            db, submission_id, status=body.status.value, feedback=body.feedback
        )
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found") from exc


# ---- Datasets ----


@router.get("/datasets", response_model=list[AdminDatasetRead])
async def list_admin_datasets(db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)):
    return await admin_service.list_all_datasets(db)


@router.patch("/datasets/{dataset_id}", response_model=AdminDatasetRead)
async def update_dataset(
    dataset_id: uuid.UUID,
    body: AdminDatasetUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(require_admin),
):
    try:
        return await admin_service.update_dataset(db, dataset_id, **body.model_dump())
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found") from exc


@router.delete("/datasets/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: CurrentUser = Depends(require_admin)
):
    try:
        await admin_service.delete_dataset(db, dataset_id)
    except admin_service.NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found") from exc
