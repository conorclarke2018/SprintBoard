from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, utcnow
from app.models.enums import ProjectStatus

if TYPE_CHECKING:
    from app.models.issue import Issue
    from app.models.sprint import Sprint
    from app.models.user import User


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    key: Mapped[str] = mapped_column(String(5), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(10), default=ProjectStatus.PENDING, index=True)
    review_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    owner: Mapped["User"] = relationship(back_populates="projects")
    issues: Mapped[list["Issue"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="Issue.number"
    )
    sprints: Mapped[list["Sprint"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="Sprint.start_date"
    )

    @property
    def is_approved(self) -> bool:
        return self.status == ProjectStatus.APPROVED

    @property
    def issue_count(self) -> int:
        return len(self.issues)
