import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

export default function App() {
  return (
    <div style = {{fontFamily: "system-ui", padding: 24}}>
      <h1>IV Events</h1>
      <p>The React Frontend is Running!</p>
      <p>URL Path: {window.location.pathname}</p>
    </div>
  )
}