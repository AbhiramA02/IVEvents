import { useEffect, useState } from "react";
import "./App.css";

function AuthButtons() {
  const startGoogle = () => {
    // full redirect to backend start endpoint
    window.location.href = "/auth/google/start";
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", marginTop: 12 }}>
      <button onClick={startGoogle}>Login</button>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [events, setEvents] = useState([]);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [eventsError, setEventsError] = useState("");
  const [toggling, setToggling] = useState({});
  //const [status, setStatus] = useState("Checking session...");

  useEffect(() => {
    fetch("/auth/me", { credentials: "include" })
      .then(async (r) => {
        const data = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(data?.error || `HTTP ${r.status}`);
        return data;
      })
      .then((data) => {
        setUser(data.user);
        //setStatus(data.user ? "Logged in" : "Not logged in");
      })
      .catch((e) => {
        setUser(null);
        //setStatus(`Session check failed: ${e.message}`);
      });
  }, []);

  const loadEvents = () => {
    setEventsLoading(true);
    setEventsError("");

    fetch("/events", {credentials: "include"})
      .then(async (r) => {
        const data = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(data?.error || `HTTP ${r.status}`);
        return data;
      })
      .then((data) => {
        setEvents(Array.isArray(data.events) ? data.events : []);
      })
      .catch((e) => {
        setEventsError(e.message || "Failed to load events.");
        setEvents([]);
      })
      .finally(() => {
        setEventsLoading(false);
      });
  };

  useEffect(() => {
    loadEvents();
  }, []);

  const logout = () => {
    fetch("/auth/logout", {
      method: "POST",
      credentials: "include",
    }).then(() => {
      setUser(null);
    })
  }

  /**
   * Update interest status for given event
   * If  `shouldBeInterested` is true: POST /events/<event_id>/interest
   * Else DELETE /events/<event_id>/interest
   * 
   * The backend returns: {event_id, viewer_interest, interest_count}
   */

  const setInterest = async (eventId, shouldBeInterested) => {
    const method = shouldBeInterested ? "POST" : "DELETE";

    const res = await fetch(`/events/${eventId}/interest`, {
      method,
      credentials: "include",
    });

    //If user isn't logged in, backend returns 401
    if (res.status === 401) {
      alert("Please log in to mark interest.");
      return null;
    }

    if (!res.ok) {
      const text = await res.text();
      console.error("Interest update failed:", res.status, text);
      alert("Could not update interest. Try again.");
      return null;
    }

    return await res.json();
  };

  /**
   * When user clicks the Interested button:
   * Decide whether we are turning interest on or off based on current state
   * Call the backend endpoint
   * Update the matching event card in state with returned count + viewer_interest
   */

  const onInterestedClick = async (eventObj) => {
    //Prevent spamming the same button while request in flight
    if (toggling[eventObj.id]) return;

    //Determine current interest state for this viewer
    const currentlyInterested = eventObj.viewer_interest === "interested";
    const shouldBeInterested = !currentlyInterested;

    //Mark this event as "toggling" to disable the button temporarily
    setToggling((prev) => ({ ...prev, [eventObj.id]: true}));

    try {
      const data = await setInterest(eventObj.id, shouldBeInterested);
      if (!data) return;

      setEvents((prev) => 
        prev.map((e) => 
          e.id === data.event_id
          ? {
            ...e,
            viewer_interest: data.viewer_interest,
            interest_count: data.interest_count,
          }
          : e
        )
      );
    } finally {
      //Always clear toggling state even if request failed
      setToggling((prev) => ({ ...prev, [eventObj.id]: false}));
    }
  };

  return (
    <div style={{ fontFamily: "system-ui", padding: 24 }}>
      <h1>IV Events</h1>
      <p>See what's going on in and around UC Santa Barbara!</p>

      {user ? (
        <div>
          <div>Logged in as {user.email}.</div>
          <button 
          onClick={logout}
          style={{marginTop: 12}}
          >
            Logout
          </button>
        </div>
      ) : (
        <>
          <div>Not logged in.</div>
          <AuthButtons />
        </>
      )}

      <hr style={{margin: "24px 0", opacity: 0.2}}/>
      <div style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>
        <h2 style={{margin: 0}}>Upcoming Events</h2>

        <button onClick={loadEvents} disabled={eventsLoading}>
          Refresh
        </button>
      </div>

      {eventsLoading && <div style = {{marginTop: 12}}>Loading Events...</div>}
      {eventsError && (
        <div style = {{marginTop:12}}>
          Error Loading Events: {eventsError}
        </div>
      )}

      {!eventsLoading && !eventsError && events.length === 0 && (
        <div style={{marginTop: 12, opacity: 0.8}}>No Events Found.</div>
      )}

      <div style = {{display: "grid", gap: 12, marginTop: 12, gridTemplateColumns: "repeat(3, minmax(0, 1fr))", alignItems: "start",}}>
        {events.map((e) => (
          <div 
          key = {e.id}
          style = {{
            border: "1px solid rgba(255, 255, 255, 0.15)",
            borderRadius: 10,
            padding: 12,
          }}>
            <div style={{fontSize: 18, fontWeight: 700}}>{e.title}</div>
            {e.location && <div style = {{marginTop: 6, opacity: 0.8}}> {e.location}</div>}
            {e.start_time && (
              <div style = {{marginTop: 6, opacity: 0.8}}>
                {new Date(e.start_time).toLocaleString()}
              </div>
            )}

            {e.description && <div style={{marginTop: 8}}>{e.description}</div>}

            <div style = {{marginTop: 10, opacity: 0.85}}>
              Interest Count: {e.interest_count ?? 0}
            </div>

            <button onClick={() => onInterestedClick(e)}
            disabled = {!!toggling[e.id]}
            style={{marginTop : 10}}>
              {e.viewer_interest === "interested" ? "Interested ✓" : "Interested"}
            </button>


            {/*<div style = {{marginTop: 6, opacity: 0.85}}>
              Your Interest: {e.viewer_interest ?? "none"}
            </div>*/}
          </div>
        ))}
      </div>
    </div>
  );
}
