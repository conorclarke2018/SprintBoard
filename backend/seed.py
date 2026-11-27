"""Add the demo data by hand: uv run python seed.py

The app also does this automatically on startup when the database has an admin but no projects.
"""

import sys

from app import models  # noqa: F401  (registers all tables)
from app.database import Base, SessionLocal, engine
from app.demo_data import DEMO_PASSWORD, create_demo_data, needs_demo_data
from app.models import User
from app.models.enums import UserRole

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.query(User).filter(User.role == UserRole.ADMIN).first() is None:
            sys.exit("No admin yet. Register the first account in the app, then run this again.")
        if not needs_demo_data(db):
            sys.exit("Projects already exist, so the demo data was not added.")
        create_demo_data(db)
        print(f"Demo data added. Demo accounts use the password '{DEMO_PASSWORD}'.")
