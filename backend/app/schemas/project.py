import re
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

from app.models.enums import ProjectStatus
from app.schemas.common import BlankToNone
from app.schemas.user import UserRead

PROJECT_KEY_PATTERN = re.compile(r"^[A-Z]{2,5}$")

ProjectName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=100)]
ProjectDescription = Annotated[
    Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)] | None, BlankToNone
]
RejectReason = Annotated[
    Annotated[str, StringConstraints(strip_whitespace=True, max_length=300)] | None, BlankToNone
]


class ProjectUpdate(BaseModel):
    name: ProjectName
    description: ProjectDescription = None


class ProjectCreate(ProjectUpdate):
    key: str

    @field_validator("key", mode="before")
    @classmethod
    def check_key(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip().upper()
            if not PROJECT_KEY_PATTERN.match(value):
                raise ValueError("Key must be 2 to 5 letters, for example SB")
        return value


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    key: str
    description: str | None
    status: ProjectStatus
    review_note: str | None
    created_at: datetime
    issue_count: int
    owner: UserRead


class ProjectReject(BaseModel):
    reason: RejectReason = None
