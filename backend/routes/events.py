from flask import Blueprint, jsonify, request
import uuid
from sqlalchemy import func
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


@events_bp.get("/debug/whoami")
def debug_whoami():
  user_id = get_current_user_id() #Use same helper your /events endpoint uses
  return jsonify({"user_id": str(user_id) if user_id else None}), 200 #Return user_id so you can confirm whether login is recognized