def iso(dt):
  return dt.isoformat() if dt else None

"""Helpers to convert SQLAlchemy models to JSON-safe dicts."""
def event_to_dict(event, interest_count = 0, viewer_interest = None):
  return {
    "id": str(event.id),
    "title": event.title,
    "description": event.description,
    "location": event.location,
    "start_time": iso(event.start_time),
    "end_time": iso(event.end_time),
    "organizer": event.organizer,
    "category": event.category,
    "image_url": event.image_url,
    "source": event.source,
    "created_at": iso(event.created_at),
    "updated_at": iso(event.updated_at),
    "interest_count": int(interest_count or 0),
    "viewer_interest": viewer_interest,
  }