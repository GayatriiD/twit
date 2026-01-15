import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import TweetDisplay from './components/TweetDisplay'
import AdminPanel from './components/AdminPanel'

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<TweetDisplay />} />
                <Route path="/admin" element={<AdminPanel />} />
            </Routes>
        </Router>
    )
}

export default App
