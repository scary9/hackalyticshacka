import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Processing from './pages/Processing'
import Result from './pages/Result'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/processing/:jobId" element={<Processing />} />
        <Route path="/result/:jobId" element={<Result />} />
      </Routes>
    </Router>
  )
}

export default App
