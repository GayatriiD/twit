"""Clean up mock tweets from database."""

from database import SessionLocal
from models import Tweet, DisplayedTweet

def clean_mock_tweets():
    """Remove all mock tweets from the database."""
    db = SessionLocal()
    try:
        # Delete mock tweets from tweets table
        deleted_tweets = db.query(Tweet).filter(Tweet.tweet_id.like('mock_%')).delete()
        
        # Delete mock tweets from displayed_tweets table
        deleted_displayed = db.query(DisplayedTweet).filter(DisplayedTweet.tweet_id.like('mock_%')).delete()
        
        db.commit()
        
        print(f"✓ Deleted {deleted_tweets} mock tweets from tweets table")
        print(f"✓ Deleted {deleted_displayed} mock tweets from displayed_tweets table")
        print(f"✓ Total cleaned: {deleted_tweets + deleted_displayed} records")
        
    except Exception as e:
        print(f"❌ Error cleaning mock tweets: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Cleaning mock tweets from database...")
    clean_mock_tweets()
    print("Done!")
