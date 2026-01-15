Twitter Feed Display System

A production-grade application for displaying Twitter (X) feeds on an extended monitor with persistent deduplication, automatic refresh, and QR code integration, using RapidAPI for tweet fetching.

🎯 Key Features

Full-Screen Tweet Display for extended monitors

Persistent Deduplication (no tweet repeats, even after restart)

Automatic Hourly Refresh of tweets

QR Codes linking to original tweets

Manual Controls & Keyboard Shortcuts

Admin Panel for managing Twitter handles

Mock Data Fallback when API limits are reached

Modern Dark UI with smooth animations

🏗️ Architecture Overview

Frontend: React
Backend: FastAPI (Python)
Database: PostgreSQL
Twitter Data: RapidAPI (twitter154.p.rapidapi.com)

React Frontend → FastAPI Backend → PostgreSQL
                    ↓
        RapidAPI (twitter154) / Mock Data

🗄️ Database Schema (Summary)

twitter_handles – Configured Twitter accounts

tweets – All fetched tweets with display status

displayed_tweets – Persistent deduplication tracking

🚀 Quick Start
Prerequisites

Python 3.9+

Node.js 18+

PostgreSQL 12+

RapidAPI key (Twitter API)

Backend Setup
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt

copy .env.example .env   # Add RapidAPI key
python init_db.py
python main.py


Backend: http://localhost:8000

Frontend Setup
cd frontend
npm install
npm run dev


Frontend: http://localhost:5173

🖥️ Usage
Full-Screen Display

Open the frontend in a browser

Move it to the extended monitor

Press F11 for fullscreen

Tweets auto-rotate every 30 seconds

Keyboard Shortcuts

→ / N → Next tweet

Space → Pause / Resume

R → Manual refresh

F → Toggle fullscreen

Admin Panel

Add / remove Twitter handles

Enable / disable handles

Manually fetch new tweets

View tweet statistics

🔧 Configuration (backend/.env)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/twitter_feed_db

# RapidAPI Twitter
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=twitter154.p.rapidapi.com

# Application
REFRESH_INTERVAL_HOURS=1
USE_MOCK_DATA=false
FRONTEND_URL=http://localhost:5173

🔍 Deduplication Strategy

All fetched tweets are stored in the database

Displayed tweet IDs are tracked persistently

Already displayed tweets are excluded on fetch

Guarantees zero tweet repetition, even after restarts

🧪 Testing Checklist

Tweets display correctly

QR codes redirect to correct tweet URLs

No duplicate tweets after restart

Hourly refresh works

Admin panel CRUD operations function

Mock data fallback works

📚 Tech Stack

Frontend

React 18

Vite

Backend

FastAPI

RapidAPI (twitter154)

Pydantic

Database

PostgreSQL

📄 License

MIT License

