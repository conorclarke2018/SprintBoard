"""Demo data: at least 10 records in every table, so the app can be explored straight away.

Loaded automatically on startup when an admin exists and there are no projects yet (for example
after Render's free tier wipes the SQLite database), and can also be run by hand with seed.py.
"""

import logging
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import Issue, Project, Sprint, User
from app.models.enums import (
    IssuePriority,
    IssueStatus,
    IssueType,
    ProjectStatus,
    SprintStatus,
    UserRole,
)

logger = logging.getLogger(__name__)

# Every demo account uses this password, so markers and testers can log in as a regular user.
DEMO_PASSWORD = "sprintboard1"

# (username, approved?) - two accounts are left waiting so the approval flow can be tried.
DEMO_USERS = [
    ("alice", True),
    ("ben", True),
    ("chloe", True),
    ("daniel", True),
    ("emma", True),
    ("farah", True),
    ("george", True),
    ("hannah", True),
    ("isaac", False),
    ("jess", False),
]

# (key, name, description, owner username or None for the admin, status, review note)
DEMO_PROJECTS = [
    ("SB", "SprintBoard Development", "Building SprintBoard itself, tracked in SprintBoard.", None, ProjectStatus.APPROVED, None),
    ("HD", "IT Help Desk", "Track and resolve staff IT support requests.", "alice", ProjectStatus.APPROVED, None),
    ("ASSET", "Asset Register", "Keep a record of laptops, monitors and licences.", "ben", ProjectStatus.APPROVED, None),
    ("WEB", "Company Website", "Refresh the public website and its content.", "chloe", ProjectStatus.APPROVED, None),
    ("API", "Partner API", "A REST API that partners use to submit orders.", "daniel", ProjectStatus.APPROVED, None),
    ("MOB", "Mobile App", "The customer app for iOS and Android.", "emma", ProjectStatus.APPROVED, None),
    ("DATA", "Reporting Dashboard", "Weekly sales and support figures in one place.", "farah", ProjectStatus.APPROVED, None),
    ("SEC", "Security Review", "Fix the findings from the annual security audit.", "george", ProjectStatus.APPROVED, None),
    ("ONB", "Staff Onboarding", "A checklist app for new starters' first week.", "hannah", ProjectStatus.PENDING, None),
    ("GAME", "Office Games Night", "Organise a games night for the team.", "alice", ProjectStatus.REJECTED, "Not a software project. Please use the events calendar."),
]

# (project key, name, goal, start offset in days from today, status)
DEMO_SPRINTS = [
    ("SB", "Sprint 1", "Project skeleton, login and deployment", -35, SprintStatus.COMPLETED),
    ("SB", "Sprint 2", "Projects, issues and the board", -21, SprintStatus.COMPLETED),
    ("SB", "Sprint 3", "Sprint management and polish", -7, SprintStatus.ACTIVE),
    ("SB", "Sprint 4", "User manual and final testing", 7, SprintStatus.PLANNED),
    ("HD", "Sprint 1", "Log and assign tickets", -7, SprintStatus.ACTIVE),
    ("ASSET", "Sprint 1", "Import the current spreadsheet", -21, SprintStatus.COMPLETED),
    ("ASSET", "Sprint 2", "Assign assets to staff", -7, SprintStatus.ACTIVE),
    ("WEB", "Sprint 1", "New home page", -7, SprintStatus.ACTIVE),
    ("API", "Sprint 1", "Authentication and order endpoint", 0, SprintStatus.PLANNED),
    ("MOB", "Sprint 1", "Login and account screens", -7, SprintStatus.ACTIVE),
    ("DATA", "Sprint 1", "Connect the data sources", -7, SprintStatus.ACTIVE),
    ("SEC", "Sprint 1", "High-priority findings", -7, SprintStatus.ACTIVE),
]

# (project key, title, type, priority, points, status, sprint name or None for backlog, assignee or None)
# An assignee of "owner" means the project's owner.
DEMO_ISSUES = [
    ("SB", "Set up FastAPI and React project", IssueType.TASK, IssuePriority.HIGH, 3, IssueStatus.DONE, "Sprint 1", "owner"),
    ("SB", "Users can register and log in", IssueType.STORY, IssuePriority.HIGH, 5, IssueStatus.DONE, "Sprint 1", "owner"),
    ("SB", "Deploy app to Render", IssueType.TASK, IssuePriority.MEDIUM, 2, IssueStatus.DONE, "Sprint 1", "owner"),
    ("SB", "Create, edit and delete projects", IssueType.STORY, IssuePriority.HIGH, 3, IssueStatus.DONE, "Sprint 2", "owner"),
    ("SB", "Manage issues in the backlog", IssueType.STORY, IssuePriority.HIGH, 5, IssueStatus.DONE, "Sprint 2", "owner"),
    ("SB", "Board with To Do, In Progress and Done", IssueType.STORY, IssuePriority.HIGH, 8, IssueStatus.DONE, "Sprint 2", "owner"),
    ("SB", "Start, edit and complete sprints", IssueType.STORY, IssuePriority.MEDIUM, 5, IssueStatus.IN_PROGRESS, "Sprint 3", "owner"),
    ("SB", "Board columns overflow on small screens", IssueType.BUG, IssuePriority.MEDIUM, 1, IssueStatus.TODO, "Sprint 3", "alice"),
    ("SB", "Confirm before logging out", IssueType.STORY, IssuePriority.LOW, 1, IssueStatus.DONE, "Sprint 3", "owner"),
    ("SB", "Write user manual", IssueType.TASK, IssuePriority.MEDIUM, 3, IssueStatus.TODO, "Sprint 4", None),
    ("SB", "Error message is unclear when the server is offline", IssueType.BUG, IssuePriority.LOW, 1, IssueStatus.TODO, None, None),
    ("SB", "Comments on issues", IssueType.STORY, IssuePriority.LOW, 8, IssueStatus.TODO, None, None),
    ("HD", "Staff can log a support ticket", IssueType.STORY, IssuePriority.HIGH, 5, IssueStatus.IN_PROGRESS, "Sprint 1", "owner"),
    ("HD", "Assign a ticket to an engineer", IssueType.STORY, IssuePriority.MEDIUM, 3, IssueStatus.TODO, "Sprint 1", "ben"),
    ("HD", "Email confirmation when a ticket is closed", IssueType.STORY, IssuePriority.LOW, 3, IssueStatus.TODO, None, None),
    ("ASSET", "Import assets from spreadsheet", IssueType.TASK, IssuePriority.HIGH, 5, IssueStatus.DONE, "Sprint 1", "owner"),
    ("ASSET", "Assign a laptop to a member of staff", IssueType.STORY, IssuePriority.HIGH, 3, IssueStatus.IN_PROGRESS, "Sprint 2", "owner"),
    ("ASSET", "Serial numbers with spaces fail to save", IssueType.BUG, IssuePriority.MEDIUM, 2, IssueStatus.TODO, "Sprint 2", None),
    ("WEB", "Design the new home page", IssueType.TASK, IssuePriority.HIGH, 5, IssueStatus.DONE, "Sprint 1", "owner"),
    ("WEB", "Contact form sends to the right inbox", IssueType.STORY, IssuePriority.MEDIUM, 2, IssueStatus.TODO, "Sprint 1", None),
    ("API", "Token-based authentication", IssueType.STORY, IssuePriority.HIGH, 8, IssueStatus.TODO, "Sprint 1", "owner"),
    ("API", "POST /orders endpoint", IssueType.STORY, IssuePriority.HIGH, 5, IssueStatus.TODO, "Sprint 1", None),
    ("MOB", "Login screen", IssueType.STORY, IssuePriority.HIGH, 5, IssueStatus.IN_PROGRESS, "Sprint 1", "owner"),
    ("MOB", "App crashes when rotating on the account page", IssueType.BUG, IssuePriority.HIGH, 3, IssueStatus.TODO, "Sprint 1", None),
    ("DATA", "Connect to the sales database", IssueType.TASK, IssuePriority.HIGH, 5, IssueStatus.DONE, "Sprint 1", "owner"),
    ("DATA", "Weekly support tickets chart", IssueType.STORY, IssuePriority.MEDIUM, 3, IssueStatus.IN_PROGRESS, "Sprint 1", "owner"),
    ("SEC", "Enforce HTTPS on every service", IssueType.TASK, IssuePriority.HIGH, 3, IssueStatus.DONE, "Sprint 1", "owner"),
    ("SEC", "Remove default passwords from test servers", IssueType.BUG, IssuePriority.HIGH, 2, IssueStatus.IN_PROGRESS, "Sprint 1", "owner"),
]

SPRINT_LENGTH_DAYS = 13


def needs_demo_data(db: Session) -> bool:
    """True when the database has an admin but no projects yet."""
    has_admin = db.scalar(select(User.id).where(User.role == UserRole.ADMIN).limit(1)) is not None
    has_projects = db.scalar(select(Project.id).limit(1)) is not None
    return has_admin and not has_projects


def create_demo_data(db: Session) -> bool:
    """Add the demo users, projects, sprints and issues. Returns False if there was nothing to do."""
    if not needs_demo_data(db):
        return False

    admin = db.scalar(select(User).where(User.role == UserRole.ADMIN).order_by(User.id))
    users = _create_users(db)
    projects = _create_projects(db, admin, users)
    sprints = _create_sprints(db, projects)
    _create_issues(db, projects, sprints, users)
    db.commit()

    logger.info(
        "Demo data created: %d users, %d projects, %d sprints, %d issues",
        len(users), len(projects), len(sprints), len(DEMO_ISSUES),
    )
    return True


def _create_users(db: Session) -> dict[str, User]:
    """Create any demo accounts that don't exist yet. One hash is shared to keep start-up fast."""
    password_hash = hash_password(DEMO_PASSWORD)
    users = {}
    for username, approved in DEMO_USERS:
        user = db.scalar(select(User).where(User.username == username))
        if user is None:
            user = User(username=username, password_hash=password_hash, is_approved=approved)
            db.add(user)
        users[username] = user
    return users


def _create_projects(db: Session, admin: User, users: dict[str, User]) -> dict[str, Project]:
    projects = {}
    for key, name, description, owner, status, note in DEMO_PROJECTS:
        project = Project(
            key=key,
            name=name,
            description=description,
            owner=users[owner] if owner else admin,
            status=status,
            review_note=note,
        )
        db.add(project)
        projects[key] = project
    return projects


def _create_sprints(db: Session, projects: dict[str, Project]) -> dict[tuple[str, str], Sprint]:
    today = date.today()
    sprints = {}
    for key, name, goal, offset, status in DEMO_SPRINTS:
        start = today + timedelta(days=offset)
        sprint = Sprint(
            project=projects[key],
            name=name,
            goal=goal,
            start_date=start,
            end_date=start + timedelta(days=SPRINT_LENGTH_DAYS),
            status=status,
        )
        db.add(sprint)
        sprints[(key, name)] = sprint
    return sprints


def _create_issues(
    db: Session,
    projects: dict[str, Project],
    sprints: dict[tuple[str, str], Sprint],
    users: dict[str, User],
) -> None:
    numbers: dict[str, int] = {}
    for key, title, type_, priority, points, status, sprint, assignee in DEMO_ISSUES:
        project = projects[key]
        numbers[key] = numbers.get(key, 0) + 1
        db.add(
            Issue(
                project=project,
                number=numbers[key],
                title=title,
                type=type_,
                priority=priority,
                story_points=points,
                status=status,
                sprint=sprints[(key, sprint)] if sprint else None,
                assignee=project.owner if assignee == "owner" else users.get(assignee or ""),
            )
        )
