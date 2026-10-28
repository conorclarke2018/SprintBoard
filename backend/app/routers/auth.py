from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DbSession
from app.core.security import create_access_token
from app.schemas.user import Token, UserCreate, UserLogin, UserRead
from app.services import auth_service

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: DbSession):
    return auth_service.register_user(db, data)


@router.post("/auth/login", response_model=Token)
def login(data: UserLogin, db: DbSession):
    user = auth_service.authenticate(db, data)
    return Token(access_token=create_access_token(user.id), user=UserRead.model_validate(user))


@router.get("/auth/me", response_model=UserRead)
def me(user: CurrentUser):
    return user


@router.get("/users", response_model=list[UserRead])
def list_users(db: DbSession, _user: CurrentUser):
    """Everyone who can be assigned to an issue."""
    return auth_service.list_users(db)
