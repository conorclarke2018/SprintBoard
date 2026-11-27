from fastapi import APIRouter, status

from app.core.dependencies import AdminUser, ApprovedProject, CurrentUser, DbSession, ManagedApprovedProject
from app.schemas.sprint import SprintCompleteResult, SprintCreate, SprintRead, SprintUpdate
from app.services import project_service, sprint_service

router = APIRouter(prefix="/api", tags=["sprints"])


@router.get("/projects/{project_id}/sprints", response_model=list[SprintRead])
def list_sprints(project: ApprovedProject):
    return project.sprints


@router.post(
    "/projects/{project_id}/sprints", response_model=SprintRead, status_code=status.HTTP_201_CREATED
)
def create_sprint(data: SprintCreate, project: ManagedApprovedProject, db: DbSession):
    return sprint_service.create_sprint(db, project, data)


@router.put("/sprints/{sprint_id}", response_model=SprintRead)
def update_sprint(sprint_id: int, data: SprintUpdate, db: DbSession, user: CurrentUser):
    sprint = sprint_service.get_sprint(db, sprint_id, user)
    project_service.require_manage(sprint.project, user)
    return sprint_service.update_sprint(db, sprint, data)


@router.delete("/sprints/{sprint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sprint(sprint_id: int, db: DbSession, admin: AdminUser):
    """Admins only. Issues in the sprint go back to the backlog rather than being deleted."""
    sprint = sprint_service.get_sprint(db, sprint_id, admin)
    sprint_service.delete_sprint(db, sprint)


@router.post("/sprints/{sprint_id}/start", response_model=SprintRead)
def start_sprint(sprint_id: int, db: DbSession, user: CurrentUser):
    sprint = sprint_service.get_sprint(db, sprint_id, user)
    project_service.require_manage(sprint.project, user)
    return sprint_service.start_sprint(db, sprint)


@router.post("/sprints/{sprint_id}/complete", response_model=SprintCompleteResult)
def complete_sprint(sprint_id: int, db: DbSession, user: CurrentUser):
    sprint = sprint_service.get_sprint(db, sprint_id, user)
    project_service.require_manage(sprint.project, user)
    returned = sprint_service.complete_sprint(db, sprint)
    return SprintCompleteResult(
        sprint=SprintRead.model_validate(sprint), returned_to_backlog=returned
    )
