import uuid
from datetime import datetime, timedelta, timezone
from extensions import db

def utcnow():
  """Returns current time in UTC (consistent timestamps)."""
  return datetime.now(timezone.utc)

class User(db.Model):
  """Create Users Table with One Row per Logged In Person"""
  __tablename__ = "users"

  id = db.Column(db.Uuid, primary_key = True, default = uuid.uuid4)
  email = db.Column(db.String(255), unique = True, nullable = False, index = True)
  name = db.Column(db.String(255), nullable = True)

  created_at = db.Column(db.DateTime(timezone = True), nullable = False, default = utcnow)
  last_login_at = db.Column(db.DateTime(timezone = True), nullable = True)

class Session(db.Model):
  """Create Sessions Table with One Row per Login Session"""
  __tablename__ = "sessions"

  id = db.Column(db.Uuid, primary_key = True, default = uuid.uuid4)
  user_id = db.Column(db.Uuid, db.ForeignKey("users.id", ondelete = "CASCADE"), nullable = False, index = True)
  """ForeignKey connects table to another, ensures Session cannot exists w/o valid User"""

  created_at = db.Column(db.DateTime(timezone = True), nullable = False, default = utcnow)
  expires_at = db.Column(db.DateTime(timezone = True), nullable = False)
  revoked_at = db.Column(db.DateTime(timezone = True), nullable = True)

  user = db.relationship("User", backref = db.backref("sessions", lazy = True)) #Links User & Sessions --> user.sessions = list of sessions and sessions.user = user

  @staticmethod
  def new(user_id, days = 14):
    """Creates Session for every User Login"""
    return Session(
      user_id = user_id,
      expires_at = utcnow() + timedelta(days = days),
    )