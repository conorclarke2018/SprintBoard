from fastapi import APIRouter, status

from app.core.dependencies import ApprovedProject, CurrentUser, DbSession
from app.schemas.sprint import SprintCompleteResult, SprintCreate, SprintRead
from app.services import sprint_service

router = APIRouter(prefix="/api", tags=["sprints"])


@router.get("/projects/{project_id}/sprints", response_model=list[SprintRead])
def list_sprints(project: ApprovedProject):
    return project.sprints


@router.post(
    "/projects/{project_id}/sprints", response_model=SprintRead, status_code=status.HTTP_201_CREATED
)
def create_sprint(data: SprintCreate, project: ApprovedProject, db: DbSession):
    return sprint_service.create_sprint(db, project, data)


@router.post("/sprints/{sprint_id}/start", response_model=SprintRead)
def start_sprint(sprint_id: int, db: DbSession, user: CurrentUser):
    sprint = sprint_service.get_sprint(db, sprint_id, user)
    return sprint_service.start_sprint(db, sprint)


@router.post("/sprints/{sprint_id}/complete", response_model=SprintCompleteResult)
def complete_sprint(sprint_id: int, db: DbSession, user: CurrentUser):
    sprint = sprint_service.get_sprint(db, sprint_id, user)
    returned = sprint_service.complete_sprint(db, sprint)
    return SprintCompleteResult(
        sprint=SprintRead.model_validate(sprint), returned_to_backlog=returned
    )
