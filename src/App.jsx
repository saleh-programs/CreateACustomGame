import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Dashboard from './pages/Dashboard'
import Creating from './pages/Creating'

function App() {

  return (
    <>
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard/>}/>
        <Route path="/create" element={<Creating/>}/>
      </Routes>
    </Router>
    </>
  )
}

export default App
