# RapidAPI Twitter Setup - twitter-api49

## 🚀 Quick Setup

### 1. Get RapidAPI Key

1. Go to https://rapidapi.com/belchiorarkad-FqvHs2EDOtP/api/twitter-api49
2. Click "Subscribe to Test"
3. Choose a plan (Free tier: 100 requests/month)
4. Copy your API key from the code snippets

### 2. Update .env

```bash
# Add your RapidAPI key
RAPIDAPI_KEY=your_actual_key_here

# Disable mock data
USE_MOCK_DATA=false
```

### 3. Restart Backend

```bash
# Stop with Ctrl+C, then:
cd backend
.\venv\Scripts\activate
python main.py
```

### 4. Verify

You should see:
```
✓ RapidAPI Key found (length: 50)
✓ RapidAPI Twitter connection successful!
```

## 📝 Important Notes

**API Used**: `twitter-api49` (different from twitter241)

**Endpoints**:
- User lookup: `POST /user-details-by-screen-name`
- User tweets: `POST /user-tweets`

**Request Format**: JSON body (not query params)

**Free Tier**: 100 requests/month

## ⚠️ Troubleshooting

### "No valid RapidAPI key found"
- Check `.env` file has `RAPIDAPI_KEY=...`
- No spaces around the `=`
- Key should be 40-50 characters long

### "401 Unauthorized"
- Invalid API key
- Not subscribed to twitter-api49
- Subscription expired

### "403 Forbidden"
- Not subscribed to this specific API
- Make sure you subscribed to "twitter-api49"

### "429 Rate Limit"
- Free tier limit reached (100/month)
- Wait for reset or upgrade plan
- System will use mock data automatically

## 💰 Pricing

- **Free**: 100 requests/month
- **Basic**: ~$10/month - 10,000 requests
- **Pro**: ~$50/month - 100,000 requests

Check RapidAPI for current pricing.
