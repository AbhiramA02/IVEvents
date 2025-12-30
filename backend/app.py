import os
import uuid
from flask import Flask, request
from datetime import datetime, timezone
from dotenv import load_dotenv
from extensions import db, migrate

load_dotenv()

"""
This file sets up the app, 
connects it to the database, 
wires in the database tools, 
and makes sure the schema-change system knows what tables you’ve defined.
"""

def create_app():
  app = Flask(__name__)

  app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
  app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

  app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only")

  db.init_app(app)
  migrate.init_app(app, db)

  import models

  from auth_routes import auth_bp, init_oauth
  init_oauth(app)
  app.register_blueprint(auth_bp)

  @app.get("/health")
  def health():
    return {"ok": True}
  
  @app.get("/me")
  def me():
    from models import User, Session

    session_id = request.cookies.get("session_id")
    if not session_id:
      return {"user": None}
    
    try:
      session_uuid = uuid.UUID(session_id)
    except ValueError:
      return {"user": None}

    s = Session.query.filter_by(id=session_uuid, revoked_at=None).first()
    if not s or (s.expires_at and s.expires_at < datetime.now(timezone.utc)):
      return {"user": None}
    
    u = db.session.get(User, s.user_id)
    if not u:
      return {"user": None}
    
    return {
      "user": {
        "id": str(u.id),
        "email": u.email,
        "name": u.name
      }
    }
  
  return app

app = create_app()