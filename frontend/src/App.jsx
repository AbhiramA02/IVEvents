import { useEffect, useState } from "react";
import "./App.css";

function AuthButtons() {
  const startGoogle = () => {
    // full redirect to backend start endpoint
    window.location.href = "/api/auth/google/start";
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", marginTop: 12 }}>
      <button onClick={startGoogle}>Login</button>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState("Checking session...");

  useEffect(() => {
    fetch("/api/me", { credentials: "include" })
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

  return (
    <div style={{ fontFamily: "system-ui", padding: 24 }}>
      <h1>IV Events</h1>
      <p>See what's going on in and around UC Santa Barbara!</p>

      <div style={{ marginBottom: 8, opacity: 0.8 }}>{status}</div>

      {user ? (
        <div>Logged in as {user.email}.</div>
      ) : (
        <>
          <div>Not logged in.</div>
          <AuthButtons />
        </>
      )}
    </div>
  );
}
