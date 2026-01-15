import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import './AdminPanel.css'

const API_BASE_URL = 'http://localhost:8000'

function AdminPanel() {
    const [handles, setHandles] = useState([])
    const [stats, setStats] = useState(null)
    const [newHandle, setNewHandle] = useState('')
    const [loading, setLoading] = useState(false)
    const [message, setMessage] = useState(null)

    // Fetch handles
    const fetchHandles = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/handles`)
            setHandles(response.data)
        } catch (err) {
            console.error('Failed to fetch handles:', err)
            showMessage('Failed to load handles', 'error')
        }
    }

    // Fetch stats
    const fetchStats = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/tweets/stats`)
            setStats(response.data)
        } catch (err) {
            console.error('Failed to fetch stats:', err)
        }
    }

    // Add handle
    const handleAddHandle = async (e) => {
        e.preventDefault()
        if (!newHandle.trim()) return

        try {
            setLoading(true)
            await axios.post(`${API_BASE_URL}/api/handles`, {
                handle: newHandle.trim(),
                is_active: true
            })
            setNewHandle('')
            await fetchHandles()
            showMessage('Handle added successfully', 'success')
        } catch (err) {
            showMessage(err.response?.data?.detail || 'Failed to add handle', 'error')
        } finally {
            setLoading(false)
        }
    }

    // Toggle handle
    const handleToggle = async (id) => {
        try {
            await axios.patch(`${API_BASE_URL}/api/handles/${id}/toggle`)
            await fetchHandles()
            showMessage('Handle status updated', 'success')
        } catch (err) {
            showMessage('Failed to update handle', 'error')
        }
    }

    // Delete handle
    const handleDelete = async (id) => {
        if (!confirm('Are you sure you want to delete this handle?')) return

        try {
            await axios.delete(`${API_BASE_URL}/api/handles/${id}`)
            await fetchHandles()
            showMessage('Handle deleted successfully', 'success')
        } catch (err) {
            showMessage('Failed to delete handle', 'error')
        }
    }

    // Manual refresh
    const handleManualRefresh = async () => {
        try {
            setLoading(true)
            showMessage('Fetching tweets...', 'info')
            const response = await axios.post(`${API_BASE_URL}/api/tweets/refresh`)
            await fetchStats()
            showMessage(`Refresh complete: ${response.data.stats.new} new tweets`, 'success')
        } catch (err) {
            showMessage('Failed to refresh tweets', 'error')
        } finally {
            setLoading(false)
        }
    }

    // Show message
    const showMessage = (text, type = 'info') => {
        setMessage({ text, type })
        setTimeout(() => setMessage(null), 5000)
    }

    // Initial load
    useEffect(() => {
        fetchHandles()
        fetchStats()
    }, [])

    return (
        <div className="admin-panel">
            {/* Header */}
            <div className="admin-header">
                <div>
                    <h1>Admin Panel</h1>
                    <p className="subtitle">Manage Twitter handles and system settings</p>
                </div>
                <Link to="/" className="back-btn">
                    ← Back to Display
                </Link>
            </div>

            {/* Message Toast */}
            {message && (
                <div className={`message-toast ${message.type}`}>
                    {message.text}
                </div>
            )}

            {/* Stats Section */}
            <div className="stats-section">
                <h2>System Statistics</h2>
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-value">{stats?.total_tweets || 0}</div>
                        <div className="stat-label">Total Tweets</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">{stats?.displayed_tweets || 0}</div>
                        <div className="stat-label">Displayed</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">{stats?.remaining_tweets || 0}</div>
                        <div className="stat-label">Remaining</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-value">{stats?.active_handles || 0}</div>
                        <div className="stat-label">Active Handles</div>
                    </div>
                </div>
                <button
                    onClick={handleManualRefresh}
                    disabled={loading}
                    className="refresh-btn-large"
                >
                    {loading ? '⏳ Refreshing...' : '🔄 Fetch New Tweets'}
                </button>
            </div>

            {/* Add Handle Section */}
            <div className="add-handle-section">
                <h2>Add Twitter Handle</h2>
                <form onSubmit={handleAddHandle} className="add-handle-form">
                    <div className="input-group">
                        <span className="input-prefix">@</span>
                        <input
                            type="text"
                            value={newHandle}
                            onChange={(e) => setNewHandle(e.target.value)}
                            placeholder="username"
                            disabled={loading}
                            className="handle-input"
                        />
                    </div>
                    <button type="submit" disabled={loading || !newHandle.trim()}>
                        Add Handle
                    </button>
                </form>
            </div>

            {/* Handles List */}
            <div className="handles-section">
                <h2>Twitter Handles ({handles.length})</h2>
                <div className="handles-list">
                    {handles.length === 0 ? (
                        <div className="empty-state">
                            <p>No Twitter handles configured yet.</p>
                            <p className="text-muted">Add a handle above to get started.</p>
                        </div>
                    ) : (
                        handles.map((handle) => (
                            <div key={handle.id} className={`handle-card ${!handle.is_active ? 'inactive' : ''}`}>
                                <div className="handle-info">
                                    <div className="handle-name">@{handle.handle}</div>
                                    <div className="handle-meta">
                                        <span className={`status-badge ${handle.is_active ? 'active' : 'inactive'}`}>
                                            {handle.is_active ? '● Active' : '○ Inactive'}
                                        </span>
                                        <span className="handle-date">
                                            Added: {new Date(handle.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>
                                <div className="handle-actions">
                                    <button
                                        onClick={() => handleToggle(handle.id)}
                                        className="toggle-btn"
                                    >
                                        {handle.is_active ? 'Disable' : 'Enable'}
                                    </button>
                                    <button
                                        onClick={() => handleDelete(handle.id)}
                                        className="delete-btn"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Info Section */}
            <div className="info-section">
                <h3>ℹ️ Information</h3>
                <ul>
                    <li>Active handles will be fetched automatically every hour</li>
                    <li>Tweets are deduplicated - no tweet will be shown twice</li>
                    <li>Use "Fetch New Tweets" to manually trigger a refresh</li>
                    <li>Disable handles to temporarily stop fetching without deleting</li>
                    <li>Mock data is used when Twitter API limits are reached</li>
                </ul>
            </div>
        </div>
    )
}

export default AdminPanel
