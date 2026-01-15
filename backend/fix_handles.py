"""Script to check and fix Twitter handles in the database."""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, check_db_connection
from models import TwitterHandle, Tweet

def check_and_fix_handles():
    """Check Twitter handles and activate them if needed."""
    
    if not check_db_connection():
        print("ERROR: Cannot connect to database!")
        return False
    
    db = SessionLocal()
    try:
        # Check existing handles
        all_handles = db.query(TwitterHandle).all()
        print(f"\n📊 Found {len(all_handles)} Twitter handles in database:")
        
        for handle in all_handles:
            status = "✅ ACTIVE" if handle.is_active else "❌ INACTIVE"
            print(f"  {status} - @{handle.handle}")
        
        # Count active handles
        active_count = sum(1 for h in all_handles if h.is_active)
        print(f"\n📈 Active handles: {active_count}/{len(all_handles)}")
        
        # If no active handles, activate all
        if active_count == 0:
            print("\n⚠️  WARNING: No active handles found!")
            print("Activating all handles...")
            
            for handle in all_handles:
                handle.is_active = True
                print(f"  ✓ Activated @{handle.handle}")
            
            db.commit()
            print("\n✅ All handles have been activated!")
        
        # Check tweets
        total_tweets = db.query(Tweet).count()
        displayed_tweets = db.query(Tweet).filter(Tweet.is_displayed == True).count()
        remaining_tweets = total_tweets - displayed_tweets
        
        print(f"\n📝 Tweet Statistics:")
        print(f"  Total tweets: {total_tweets}")
        print(f"  Displayed: {displayed_tweets}")
        print(f"  Remaining: {remaining_tweets}")
        
        # If no tweets, suggest refresh
        if total_tweets == 0:
            print("\n💡 TIP: No tweets in database. Use the 'Refresh' button in the UI to fetch tweets.")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Twitter Feed System - Database Check & Fix\n")
    success = check_and_fix_handles()
    sys.exit(0 if success else 1)
