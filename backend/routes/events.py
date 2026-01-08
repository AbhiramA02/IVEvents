from flask import Blueprint, jsonify, request
from sqlalchemy import func
from extensions import db
from models import Event, EventInterest
from serializers import event_to_dict

events_bp = Blueprint("events", __name__)

def get_current_user_id():
  return None


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