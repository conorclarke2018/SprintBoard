from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DbSession, OwnedProject
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services import project_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(db: DbSession, user: CurrentUser):
    return project_service.list_projects(db, user)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: DbSession, user: CurrentUser):
    return project_service.create_project(db, data, user)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project: OwnedProject):
    return project


@router.put("/{project_id}", response_model=ProjectRead)
def update_project(data: ProjectUpdate, project: OwnedProject, db: DbSession, user: CurrentUser):
    return project_service.update_project(db, project, data, user)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project: OwnedProject, db: DbSession):
    project_service.delete_project(db, project)
