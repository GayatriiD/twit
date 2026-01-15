"""API routes for tweet operations."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy.dialects.postgresql import insert
from services.twitter_service import TwitterService
from typing import Dict
from models import DisplayedTweet

router = APIRouter(prefix="/api/tweets", tags=["tweets"])
twitter_service = TwitterService()

@router.get("/next")
async def get_next_tweet(db: Session = Depends(get_db)) -> Dict:
    """
    Get the next undisplayed tweet.
    
    Returns:
        Tweet object or error message
    """
    tweet = twitter_service.get_next_undisplayed_tweet(db)
    
    if not tweet:
        raise HTTPException(status_code=404, detail="No undisplayed tweets available")
    
    return tweet.to_dict()

@router.post("/{tweet_id}/mark-displayed")
async def mark_tweet_displayed(tweet_id: str, db: Session = Depends(get_db)) -> Dict:
    """
    Mark a tweet as displayed.
    
    Args:
        tweet_id: Tweet ID to mark
        
    Returns:
        Success message
    """
    success = twitter_service.mark_tweet_as_displayed(db, tweet_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Tweet not found or already displayed")
    
    return {"message": "Tweet marked as displayed", "tweet_id": tweet_id}
    '''stmt = insert(DisplayedTweet).values(tweet_id=tweet_id)
    stmt = stmt.on_conflict_do_nothing(index_elements=["tweet_id"])

    db.execute(stmt)
    db.commit()

    return {
        "status": "ok",
        "tweet_id": tweet_id
    }'''
@router.get("/stats")
async def get_tweet_stats(db: Session = Depends(get_db)) -> Dict:
    """
    Get statistics about tweets.
    
    Returns:
        Statistics dictionary
    """
    stats = twitter_service.get_stats(db)
    return stats

@router.post("/refresh")
async def refresh_tweets(db: Session = Depends(get_db)) -> Dict:
    """
    Manually trigger tweet refresh.
    
    Returns:
        Fetch statistics
    """
    stats = twitter_service.fetch_and_store_tweets(db)
    return {
        "message": "Tweet refresh completed",
        "stats": stats
    }
