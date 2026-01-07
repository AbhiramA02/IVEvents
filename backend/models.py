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
  

class Event(db.Model):
  """This is a SQLAlchemy model representing ONE event listing - This is a 'Table'"""
  __tablename__ = "events"

  id = db.Column(db.Uuid, primary_key = True, default = uuid.uuid4) #Set Unique Integer ID for every row as Primary Key 
  
  title = db.Column(db.String(200), nullable = False) #Setting nullable = False indicates that this field is required
  description = db.Column(db.Text, nullable = True)
  location = db.Column(db.String(200), nullable = True)

  start_time = db.Column( #When timezone = True, we expect timezone-aware datetimes
    db.DateTime(timezone = True), 
    nullable = False, 
    index = True
  )
  end_time = db.Column(db.DateTime(timezone = True), nullable = False, index = True)
  
  organizer = db.Column(db.String(200), nullable = True)
  category = db.Column(db.String(80), nullable = True)

  image_url = db.Column(db.Text, nullable = True)
  source = db.Column(db.String(40), nullable = False, default = "manual")

  created_at = db.Column(
    db.DateTime(timezone = True),
    nullable = False,
    default = utcnow,
  )
  updated_at = db.Column(
    db.DateTime(timezone = True),
    nullable = False,
    default = utcnow,
    onupdate = utcnow,
  )

  interests = db.relationship(
    "EventInterest",
    backref = "event",
    cascade = "all, delete-orphan",
  )

  #Gaurdrail: end_time must be >= start_time
  __table_args__ = (
    db.CheckConstraint("end_time >= start_time", name = "ck_events_end_after_start")
  )



class EventInterest(db.Model):
  """Join talbe that stores ONE user's interest status for ONE event"""
  __tablename__ = "event_interests"

  id = db.Column(db.Uuid, primary_key = True)

  user_id = db.Column( #db.ForeignKey creates a link between event_interests and users, users.id must be existing to work
    db.Uuid, #CASCADE is so when a user is deleted, their interest rows are deleted too
    db.ForeignKey("users.id", ondelete = "CASCADE"),
    nullable = False,
  )

  event_id = db.Column(
    db.Uuid,
    db.ForeignKey("events.id", ondelete = "CASCADE"),
    nullable = False,
  )

  status = db.Column(db.String(20), nullable = False) #Interested or Not Interested

  #we add the created_at and updated_at columns because they provide important insight and functionality down the road.
  created_at = db.Column(db.DateTime(timezone = True), nullable = False, default = utcnow)
  updated_at = db.Column(db.DateTime(timezone = True), nullable = False, default = utcnow, onupdate = utcnow)

  __table_args__ = ( #Table-Level Constraints + Indexes
    db.UniqueConstraint("user_id", "event_id", name = "uq_user_event_interest"), #Prevent duplicate rows for same user/event
    db.Index("ix_event_interests_event_status", "event_id", "status") #Helpful index for fast counting
  )
