"""
extensions.py

Purpose:
- Create shared "extension objects" (like SQLAlchemy and Migrate) in one place,
  without importing the Flask app.

Why this matters:
- Lots of files need access to `db` (models, routes, auth, etc.)
- If those files import `app` directly to get `db`, you can easily create
  circular imports (A imports B imports A).
- By defining `db` here, every file can safely do: `from extensions import db`
  without pulling in the Flask app.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()