from datetime import datetime, timedelta, timezone
from app import create_app
from extensions import db
from models import Event

def seed_events():
  app = create_app() #Create Flask app using app factory
  
  with app.app_context():
    db.session.query(Event).delete() #Delete all existing Event rows so results are predictable
    now = datetime.now(timezone.utc) #Get current time in UTC, makes time consistent
    events = [ #Create a Python list of Event objects (these are NOT in the DB yet).
      #Populating all required fields
      Event(
        title = "IVEvents Kickoff Meetup",
        location = "UCSB Library",
        description = "Meet other builders and talk about roadmap.",
        start_time = now + timedelta(days = 1),
        end_time = now + timedelta(days = 1, hours = 2),
      ),

      Event(
        title = "Sunset Volleyball",
        location = "Campus Point",
        description = "Casual games, all levels welcome.",
        start_time = now + timedelta(days = 2, hours = 1),
        end_time = now + timedelta(days = 2, hours = 3),
      ),

      Event(
        title = "CS Study Jam",
        location = "HFH 1132",
        description = "Bring a problem set, leave with progress.",
        start_time = now + timedelta(days = 3, hours = 18),
        end_time = now + timedelta(days = 3, hours = 20),
      ),
    ]

    db.session.add_all(events) #Add all Event objects to the current DB session (NOT permanently saved yet).
    db.session.commit() #Commits session so the rows are written into SQLite DB.

    print(f"Seeded {len(events)} events into DB.")


#This ensures seed_events() run only when you execute this file directly (NOT when imported).
if __name__ == "__main__":
  seed_events()
