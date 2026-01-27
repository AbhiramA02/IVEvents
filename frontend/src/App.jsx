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

            <button onClick={() => alert("Clicked!")}>
              Interested
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
