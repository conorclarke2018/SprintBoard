from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, utcnow
from app.models.enums import IssuePriority, IssueStatus, IssueType

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.sprint import Sprint
    from app.models.user import User


class Issue(Base):
    __tablename__ = "issues"
    __table_args__ = (UniqueConstraint("project_id", "number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    sprint_id: Mapped[int | None] = mapped_column(
        ForeignKey("sprints.id", ondelete="SET NULL"), index=True
    )
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    number: Mapped[int]
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(10), default=IssueType.STORY)
    status: Mapped[str] = mapped_column(String(20), default=IssueStatus.TODO)
    priority: Mapped[str] = mapped_column(String(10), default=IssuePriority.MEDIUM)
    story_points: Mapped[int | None]
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    project: Mapped["Project"] = relationship(back_populates="issues")
    sprint: Mapped["Sprint | None"] = relationship(back_populates="issues")
    assignee: Mapped["User | None"] = relationship()

    @property
    def key(self) -> str:
        """Human-friendly id such as SB-12."""
        return f"{self.project.key}-{self.number}"
