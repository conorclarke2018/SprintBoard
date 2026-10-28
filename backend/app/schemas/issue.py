from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.models.enums import IssuePriority, IssueStatus, IssueType
from app.schemas.common import BlankToNone
from app.schemas.user import UserRead

StoryPoints = Literal[1, 2, 3, 5, 8, 13]
IssueTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=120)]
IssueDescription = Annotated[
    Annotated[str, StringConstraints(strip_whitespace=True, max_length=2000)] | None, BlankToNone
]


class IssueCreate(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    title: IssueTitle
    description: IssueDescription = None
    type: IssueType = IssueType.STORY
    priority: IssuePriority = IssuePriority.MEDIUM
    story_points: StoryPoints | None = None
    assignee_id: int | None = None
    sprint_id: int | None = None


class IssueUpdate(IssueCreate):
    """PUT replaces the whole issue, so status is required here."""

    status: IssueStatus


class IssueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    number: int
    project_id: int
    sprint_id: int | None
    title: str
    description: str | None
    type: IssueType
    status: IssueStatus
    priority: IssuePriority
    story_points: int | None
    assignee: UserRead | None
    created_at: datetime
    updated_at: datetime
