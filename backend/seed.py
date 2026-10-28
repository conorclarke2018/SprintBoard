"""Add demo data (a project with sprints and issues) for the admin account.

No accounts or passwords are created here. Register the first account in the app
(it becomes the admin), then run this script (from backend/):

    uv run python seed.py
"""

import sys
from datetime import date, timedelta

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Issue, Project, Sprint, User
from app.models.enums import (
    IssuePriority,
    IssueStatus,
    IssueType,
    ProjectStatus,
    SprintStatus,
    UserRole,
)

DEMO_KEY = "SB"

# (title, type, priority, points, status, sprint index or None for backlog, assigned to the admin)
DEMO_ISSUES = [
    ("Set up FastAPI and React project", IssueType.TASK, IssuePriority.HIGH, 3, IssueStatus.DONE, 0, True),
    ("Users can register and log in", IssueType.STORY, IssuePriority.HIGH, 5, IssueStatus.DONE, 0, True),
    ("Deploy app to Render", IssueType.TASK, IssuePriority.MEDIUM, 2, IssueStatus.DONE, 0, True),
    ("Create, edit and delete projects", IssueType.STORY, IssuePriority.HIGH, 3, IssueStatus.DONE, 1, False),
    ("Manage issues in the backlog", IssueType.STORY, IssuePriority.HIGH, 5, IssueStatus.IN_PROGRESS, 1, False),
    ("Board with To Do, In Progress and Done", IssueType.STORY, IssuePriority.HIGH, 8, IssueStatus.IN_PROGRESS, 1, True),
    ("Board columns overflow on small screens",IssueType.BUG, IssuePriority.MEDIUM, 1, IssueStatus.TODO, 1, True),
    ("Start and complete sprints", IssueType.STORY, IssuePriority.MEDIUM, 5, IssueStatus.TODO, 1, False),
    ("Write user manual", IssueType.TASK, IssuePriority.MEDIUM, 3, IssueStatus.TODO, None, False),
    ("Add GitHub Actions CI", IssueType.TASK, IssuePriority.LOW, 2, IssueStatus.TODO, None, True),
    ("Error message is unclear when the server is offline", IssueType.BUG, IssuePriority.LOW, 1, IssueStatus.TODO, None, False),
    ("Comments on issues", IssueType.STORY, IssuePriority.LOW, 8, IssueStatus.TODO, None, False),
]


def create_demo_data() -> None:
    with SessionLocal() as db:
        admin = db.scalar(select(User).where(User.role == UserRole.ADMIN).order_by(User.id))
        if admin is None:
            sys.exit("No admin yet. Register the first account in the app, then run this again.")
        if db.scalar(select(Project).where(Project.key == DEMO_KEY)) is not None:
            print(f"Demo project {DEMO_KEY} already exists. Nothing to do.")
            return

        project = Project(
            name="SprintBoard Development",
            key=DEMO_KEY,
            description="Building SprintBoard itself, tracked in SprintBoard.",
            owner=admin,
            status=ProjectStatus.APPROVED,
        )
        db.add(project)

        today = date.today()
        sprints = [
            Sprint(
                project=project,
                name="Sprint 1",
                goal="Project skeleton, login and deployment",
                start_date=today - timedelta(days=21),
                end_date=today - timedelta(days=8),
                status=SprintStatus.COMPLETED,
            ),
            Sprint(
                project=project,
                name="Sprint 2",
                goal="Projects, issues and the board",
                start_date=today - timedelta(days=7),
                end_date=today + timedelta(days=6),
                status=SprintStatus.ACTIVE,
            ),
        ]
        db.add_all(sprints)

        for number, (title, type_, priority, points, status, sprint, assigned) in enumerate(
            DEMO_ISSUES, start=1
        ):
            db.add(
                Issue(
                    project=project,
                    number=number,
                    title=title,
                    type=type_,
                    priority=priority,
                    story_points=points,
                    status=status,
                    sprint=sprints[sprint] if sprint is not None else None,
                    assignee=admin if assigned else None,
                )
            )

        db.commit()
        print(f"Demo project {DEMO_KEY} created for {admin.username}.")


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    create_demo_data()
