from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, utcnow
from app.models.enums import IssueStatus, SprintStatus

if TYPE_CHECKING:
    from app.models.issue import Issue
    from app.models.project import Project


class Sprint(Base):
    __tablename__ = "sprints"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(60))
    goal: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[date]
    end_date: Mapped[date]
    status: Mapped[str] = mapped_column(String(20), default=SprintStatus.PLANNED)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    project: Mapped["Project"] = relationship(back_populates="sprints")
    issues: Mapped[list["Issue"]] = relationship(back_populates="sprint")

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def done_count(self) -> int:
        return sum(1 for issue in self.issues if issue.status == IssueStatus.DONE)
