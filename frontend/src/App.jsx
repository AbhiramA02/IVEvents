import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import Navbar from "./components/Navbar"
import './App.css'

function AuthButtons() {
  const startGoogle = () => {
    window.location.href = "/auth/google/start";
  };

  return (
    <div style = {{display: "flex", gap: 12}}>
      <button onClick={startGoogle}>Login</button>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch("/me", {credentials: "include"})
    .then((r) => r.json())
    .then((data) => setUser(data.user));
  }, []);

  return (
    <div style = {{fontFamily: "system-ui", padding: 24}}>
      <h1>IV Events</h1>
      <p>See what's going on in and around UC Santa Barbara!</p>
      {user ? (
        <div>Logged in as {user.email}.</div>
      ) : (
        <>
          <div>Not logged in.</div>
          <AuthButtons/>
        </>
        )}
    </div>
  )
}