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
    </div>
  );
}
