import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import AssessmentFlow from './pages/AssessmentFlow'
import ResultsDashboard from './pages/ResultsDashboard'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/assessment" element={<AssessmentFlow />} />
          <Route path="/results" element={<ResultsDashboard />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
