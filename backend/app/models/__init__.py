"""Import every model so SQLAlchemy knows about all tables before create_all()."""

from app.models.issue import Issue
from app.models.project import Project
from app.models.sprint import Sprint
from app.models.user import User

__all__ = ["Issue", "Project", "Sprint", "User"]
