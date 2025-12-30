import os
from datetime import datetime, timezone
from flask import Blueprint, redirect, make_response, request
from authlib.integrations.flask_client import OAuth

from extensions import db
from models import User, Session

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
oauth = OAuth()

def init_oauth(app):
  oauth.init_app(app)
  oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration", 
    client_kwargs={"scope": "openid email profile"},
  )

@auth_bp.get("/google/start")
def google_start(): #Sends User to Login Screen
  redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
  return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.get("/google/callback")
def google_callback(): #Handler to redirect back to app after Login
  token = oauth.google.authorize_access_token()
  userinfo = token.get("userinfo") or {}

  email = userinfo.get("email")
  name = userinfo.get("name")

  if not email:
    return {"error": "No email returned from Google."}, 400
  
  user = User.query.filter_by(email=email).first()
  now = datetime.now(timezone.utc)

  if user:
    user.last_login_at = now
    user.name = name or user.name
  else:
    user = User(email = email, name = name, last_login_at = now)
    db.session.add(user)
    db.session.flush()

  session = Session.new(user_id=user.id, days = 14)
  db.session.add(session)
  db.session.commit()

  frontend_url = os.getenv("FRONTEND_URL", "/")
  resp = make_response(redirect(frontend_url))
  is_prod = os.getenv("FLASK_ENV") == "production"

  resp.set_cookie(
    "session_id",
    str(session.id),
    httponly=True,
    secure=is_prod,
    samesite="Lax",
    max_age=14*24*60*60,
    path="/"
  )
  return resp

@auth_bp.post("/logout")
def logout(): #For User Logouts 
  session_id = request.cookies.get("session_id")
  resp = make_response({"ok": True})

  resp.set_cookie("session_id", "", expires=0, path="/")

  if not session_id:
    return resp
  
  s = Session.query.filter_by(id=session_id, revoked_at=None).first()
  if s:
    s.revoked_at = datetime.now(timezone.utc)
    db.session.commit()

  return resp