import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { QRCodeSVG } from 'qrcode.react'
import axios from 'axios'
import './TweetDisplay.css'

const API_BASE_URL = 'http://localhost:8000'

function TweetDisplay() {
    const [currentTweet, setCurrentTweet] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [isPaused, setIsPaused] = useState(false)
    const [stats, setStats] = useState(null)
    const [autoRotateInterval, setAutoRotateInterval] = useState(30000) // 30 seconds

    // Fetch next tweet
    const fetchNextTweet = useCallback(async () => {
        try {
            setLoading(true)
            setError(null)

            // IMPORTANT: Mark current tweet as displayed BEFORE fetching next
            // This prevents the infinite loop where the same tweet keeps appearing
            if (currentTweet) {
                await axios.post(`${API_BASE_URL}/api/tweets/${currentTweet.tweet_id}/mark-displayed`)
            }

            // Now fetch the next undisplayed tweet
            const response = await axios.get(`${API_BASE_URL}/api/tweets/next`)

            setCurrentTweet(response.data)
            setLoading(false)
        } catch (err) {
            if (err.response?.status === 404) {
                setError('No more tweets available. Please refresh to fetch new tweets.')
            } else {
                setError('Failed to load tweet. Please try again.')
            }
            setLoading(false)
        }
    }, [currentTweet])

    // Fetch stats
    const fetchStats = useCallback(async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/tweets/stats`)
            setStats(response.data)
        } catch (err) {
            console.error('Failed to fetch stats:', err)
        }
    }, [])

    // Manual refresh (fetch new tweets from Twitter)
    const handleManualRefresh = async () => {
        try {
            setLoading(true)
            await axios.post(`${API_BASE_URL}/api/tweets/refresh`)
            await fetchStats()
            await fetchNextTweet()
        } catch (err) {
            setError('Failed to refresh tweets')
            setLoading(false)
        }
    }

    // Initial load
    useEffect(() => {
        fetchNextTweet()
        fetchStats()
    }, [])

    // Auto-rotation
    useEffect(() => {
        if (isPaused || !currentTweet) return

        const interval = setInterval(() => {
            fetchNextTweet()
        }, autoRotateInterval)

        return () => clearInterval(interval)
    }, [isPaused, currentTweet, autoRotateInterval, fetchNextTweet])

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyPress = (e) => {
            switch (e.key) {
                case 'ArrowRight':
                case 'n':
                    fetchNextTweet()
                    break
                case ' ':
                    e.preventDefault()
                    setIsPaused(prev => !prev)
                    break
                case 'r':
                    handleManualRefresh()
                    break
                case 'f':
                    if (document.fullscreenElement) {
                        document.exitFullscreen()
                    } else {
                        document.documentElement.requestFullscreen()
                    }
                    break
                default:
                    break
            }
        }

        window.addEventListener('keydown', handleKeyPress)
        return () => window.removeEventListener('keydown', handleKeyPress)
    }, [fetchNextTweet])

    // Format timestamp
    const formatTimestamp = (timestamp) => {
        if (!timestamp) return ''
        const date = new Date(timestamp)
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    return (
        <div className="tweet-display-container">
            {/* Header with controls */}
            <div className="controls-header">
                <div className="stats">
                    {stats && (
                        <>
                            <span className="stat-item">
                                <span className="stat-label">Total:</span> {stats.total_tweets}
                            </span>
                            <span className="stat-item">
                                <span className="stat-label">Displayed:</span> {stats.displayed_tweets}
                            </span>
                            <span className="stat-item">
                                <span className="stat-label">Remaining:</span> {stats.remaining_tweets}
                            </span>
                        </>
                    )}
                </div>

                <div className="controls">
                    <button onClick={fetchNextTweet} disabled={loading} className="control-btn">
                        Next →
                    </button>
                    <button onClick={() => setIsPaused(!isPaused)} className="control-btn">
                        {isPaused ? '▶ Resume' : '⏸ Pause'}
                    </button>
                    <button onClick={handleManualRefresh} disabled={loading} className="control-btn">
                        🔄 Refresh
                    </button>
                    <a href="/admin" className="control-btn admin-link">
                        ⚙️ Admin
                    </a>
                </div>
            </div>

            {/* Main tweet display */}
            <div className="tweet-display-main">
                <AnimatePresence mode="wait">
                    {loading && !currentTweet ? (
                        <motion.div
                            key="loading"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="loading-state"
                        >
                            <div className="spinner"></div>
                            <p>Loading tweet...</p>
                        </motion.div>
                    ) : error ? (
                        <motion.div
                            key="error"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="error-state"
                        >
                            <h2>⚠️ {error}</h2>
                            <button onClick={handleManualRefresh} className="refresh-btn">
                                Refresh Tweets
                            </button>
                        </motion.div>
                    ) : currentTweet ? (
                        <motion.div
                            key={currentTweet.tweet_id}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            transition={{ duration: 0.5 }}
                            className="tweet-card"
                        >
                            {/* Tweet Header */}
                            <div className="tweet-header">
                                <div className="author-info">
                                    <h2 className="author-name">{currentTweet.author_name || currentTweet.author_handle}</h2>
                                    <p className="author-handle">@{currentTweet.author_handle}</p>
                                </div>
                                <div className="tweet-timestamp">
                                    {formatTimestamp(currentTweet.created_at_twitter)}
                                </div>
                            </div>

                            {/* Tweet Content */}
                            <div className="tweet-content">
                                <p className="tweet-text">{currentTweet.text}</p>
                            </div>

                            {/* Media if available */}
                            {currentTweet.media_url && (
                                <div className="tweet-media">
                                    <img src={currentTweet.media_url} alt="Tweet media" />
                                </div>
                            )}

                            {/* QR Code Section */}
                            <div className="qr-section">
                                <div className="qr-code-container">
                                    <QRCodeSVG
                                        value={currentTweet.tweet_url}
                                        size={200}
                                        level="H"
                                        includeMargin={true}
                                        bgColor="#ffffff"
                                        fgColor="#000000"
                                    />
                                </div>
                                <div className="qr-info">
                                    <p className="qr-label">Scan to view on Twitter</p>
                                    <p className="qr-url">{currentTweet.tweet_url}</p>
                                </div>
                            </div>
                        </motion.div>
                    ) : null}
                </AnimatePresence>
            </div>

            {/* Footer with keyboard shortcuts */}
            <div className="footer-hints">
                <span>→ or N: Next</span>
                <span>Space: Pause/Resume</span>
                <span>R: Refresh</span>
                <span>F: Fullscreen</span>
            </div>

            {/* Pause indicator */}
            {isPaused && (
                <div className="pause-indicator">
                    ⏸ PAUSED
                </div>
            )}
        </div>
    )
}

export default TweetDisplay
