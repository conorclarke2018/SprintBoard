from fastapi import APIRouter, status
from sqlalchemy import select

from app.core.dependencies import AdminUser, DbSession
from app.models import User
from app.schemas.project import ProjectRead, ProjectReject
from app.schemas.user import AdminUserRead, RoleUpdate
from app.services import project_service, user_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[AdminUserRead])
def list_users(db: DbSession, _admin: AdminUser):
    return list(db.scalars(select(User).order_by(User.username)))


@router.post("/users/{user_id}/approve", response_model=AdminUserRead)
def approve_user(user_id: int, db: DbSession, admin: AdminUser):
    user = user_service.get_user(db, user_id)
    return user_service.approve_user(db, user, admin)


@router.put("/users/{user_id}/role", response_model=AdminUserRead)
def change_role(user_id: int, data: RoleUpdate, db: DbSession, admin: AdminUser):
    user = user_service.get_user(db, user_id)
    return user_service.set_role(db, user, data.role, admin)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: DbSession, admin: AdminUser):
    user = user_service.get_user(db, user_id)
    user_service.delete_user(db, user, admin)


@router.get("/project-requests", response_model=list[ProjectRead])
def list_project_requests(db: DbSession, _admin: AdminUser):
    return project_service.list_requests(db)


@router.post("/projects/{project_id}/approve", response_model=ProjectRead)
def approve_project(project_id: int, db: DbSession, admin: AdminUser):
    project = project_service.get_project(db, project_id, admin)
    return project_service.approve_project(db, project, admin)


@router.post("/projects/{project_id}/reject", response_model=ProjectRead)
def reject_project(project_id: int, data: ProjectReject, db: DbSession, admin: AdminUser):
    project = project_service.get_project(db, project_id, admin)
    return project_service.reject_project(db, project, data.reason, admin)
