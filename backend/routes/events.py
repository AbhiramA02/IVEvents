from flask import Blueprint, jsonify, request
import uuid #Used to validate + parse UUID strings into UUID objects
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Event, EventInterest, Session
from serializers import event_to_dict

events_bp = Blueprint("events", __name__)

def get_current_user_id(): #Follows similar structure to /me authentication route
  session_id = request.cookies.get("session_id") #Read the session_id cookie that was set during Google login
  
  #If there's no cookie, the viewer is not logged in
  if not session_id: 
    return None
  
  #Convert the cookie string to a UUID; if invalid, treat as logged out.
  try:
    session_uuid = uuid.UUID(session_id)
  except ValueError:
    return None
  
  #Look up the session in the DB, making sure it has not been revoked.
  s = Session.query.filter_by(id=session_uuid, revoked_at=None).first()

  #If the session doesn't exist or doesn't map to a real user, treat as logged out.
  if not s or not s.user:
    return None
  
  return s.user.id #Get the UUID of the logged-in user (same as /me endpoint returns).

@events_bp.get("/events")
def list_events():
  user_id = get_current_user_id() # Identify who is currently logged in

  events = (
    db.session.query(Event)
    .order_by(Event.start_time.asc())
    .all()
  )

  if not events:
    return jsonify({"events": []}), 200
  
  event_ids = [e.id for e in events]

  count_rows = ( # 1. Count "interested" per event
    db.session.query(
      EventInterest.event_id,
      func.count().label("cnt")
    )
    .filter(EventInterest.event_id.in_(event_ids))
    .filter(EventInterest.status == "interested")
    .group_by(EventInterest.event_id)
    .all()
  )

  counts_map = {row.event_id: row.cnt for row in count_rows}


  viewer_map = {} # 2. Compute viewer_interest per event (only for the current user)

  if user_id:
    viewer_rows = (
      db.session.query(EventInterest.event_id, EventInterest.status)
      .filter(EventInterest.user_id == user_id)
      .filter(EventInterest.event_id.in_(event_ids))
      .all()
    )

    viewer_map = {row.event_id: row.status for row in viewer_rows}
  
  
  payload = [ # 3. Build the final JSON response list
    event_to_dict(
      e,
      interest_count = counts_map.get(e.id, 0),
      viewer_interest = viewer_map.get(e.id),
    )
    for e in events
  ]

  return jsonify({"events": payload}), 200

@events_bp.route("/events/<event_id>/interest", methods=["POST"]) #Lets currently logged-in user toggle interest for event.
def add_interest(event_id):
  """
  Marks interest for the currently logged-in user on the given event.
  Idempotent Behaviour:
  - If the user already marked interest, we return success without creating a duplicate row.
  """

  #Identify which user is logged in via session cookie helper
  user_id = get_current_user_id()
  if not user_id:
    return jsonify({"error": "Not authenticated"}), 401
  
  #Convert the URL string to a UUID object (and validate format)
  try:
    event_uuid = uuid.UUID(event_id)
  except ValueError:
    return jsonify({"error": "Invalid event id"}), 400
  
  #Ensure the event exists
  event = Event.query.get(event_uuid)
  if not event:
    return jsonify({"error": "Event not found"}), 404
  
  #Look up the specific interest row for this (user, event)
  existing = EventInterest.query.filter_by(user_id=user_id, event_id=event_uuid).first()
  if existing:
    count = EventInterest.query.filter_by(event_id=event_uuid, status="interested").count()

    return jsonify({
      "event_id": str(event_uuid),
      "viewer_interest": "interested",
      "interest_count": count
    }), 200
  
  db.session.add(EventInterest(
    user_id=user_id,
    event_id=event_uuid,
    status="interested"
  ))

  try:
    db.session.commit()
  except IntegrityError:
    db.session.rollback()

  count = EventInterest.query.filter_by(event_id=event_uuid, status="interested").count()

  return jsonify({
    "event_id": str(event_uuid),
    "viewer_interest": "interested",
    "interest_count": count
  }), 201

@events_bp.route("/events/<event_id>/interest", methods=["DELETE"])
def remove_interest(event_id):
  """
  Unmarks interest for the currently logged-in user on the given event.
  Idempotent Behaviour:
  - If the user wasn't interested, return success anyway (no error).
  """

  #Identify which user is logged in via session cookie helper
  user_id = get_current_user_id()
  if not user_id:
    return jsonify({"error": "Not authenticated"}), 401
  
  #Convert the URL string to a UUID object (and validate format)
  try:
    event_uuid = uuid.UUID(event_id)
  except ValueError:
    return jsonify({"error": "Invalid event id"}), 400
  
  #Ensure the event exists
  event = Event.query.get(event_uuid)
  if not event:
    return jsonify({"error": "Event not found"}), 404
  
  #Look up the specific interest row for this (user, event)
  existing = EventInterest.query.filter_by(user_id=user_id, event_id=event_uuid).first()
  if existing:
    db.session.delete(existing)
    db.session.commit()

  count = EventInterest.query.filter_by(event_id=event_uuid, status="interested").count()

  return jsonify({
    "event_id": str(event_uuid),
    "viewer_interest": None,
    "interest_count": count
  }), 200

@events_bp.get("/debug/whoami")
def debug_whoami():
  user_id = get_current_user_id() #Use same helper your /events endpoint uses
  return jsonify({"user_id": str(user_id) if user_id else None}), 200 #Return user_id so you can confirm whether login is recognized