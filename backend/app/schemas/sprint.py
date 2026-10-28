from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

from app.models.enums import SprintStatus
from app.schemas.common import BlankToNone

SprintName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=60)]
SprintGoal = Annotated[
    Annotated[str, StringConstraints(strip_whitespace=True, max_length=300)] | None, BlankToNone
]


class SprintCreate(BaseModel):
    name: SprintName
    goal: SprintGoal = None
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def check_dates(self) -> "SprintCreate":
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after the start date")
        return self


class SprintRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    goal: str | None
    start_date: date
    end_date: date
    status: SprintStatus
    issue_count: int
    done_count: int


class SprintCompleteResult(BaseModel):
    sprint: SprintRead
    returned_to_backlog: int
