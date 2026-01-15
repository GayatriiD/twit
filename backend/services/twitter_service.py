"""Twitter service for fetching and managing tweets."""

import os
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models import Tweet, DisplayedTweet, TwitterHandle
import random

class TwitterService:
    """Service for interacting with Twitter API via RapidAPI."""
    
    def __init__(self):
        """Initialize Twitter service with RapidAPI."""
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        self.use_mock_data = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
        
        # RapidAPI Twitter API endpoints
        # Using "twitter241" API from RapidAPI
        self.rapidapi_host = "twitter241.p.rapidapi.com"
        self.api_base_url = f"https://{self.rapidapi_host}"
        
        # Validate RapidAPI key
        if self.rapidapi_key and len(self.rapidapi_key) > 20:
            print(f"✓ RapidAPI Key found (length: {len(self.rapidapi_key)})")
            # Test the connection if not using mock data
            if not self.use_mock_data:
                if self._test_rapidapi_connection():
                    print("✓ RapidAPI Twitter connection successful!")
                else:
                    print("⚠ RapidAPI connection failed, falling back to mock data")
                    self.use_mock_data = True
        else:
            print("⚠ No valid RapidAPI key found, using mock data")
            self.use_mock_data = True
    
    def _get_rapidapi_headers(self) -> dict:
        """Get headers for RapidAPI requests."""
        return {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": self.rapidapi_host,
            "Content-Type": "application/json"
        }
    
    def _test_rapidapi_connection(self) -> bool:
        """Test RapidAPI connection."""
        try:
            headers = self._get_rapidapi_headers()
            
            # Test with a simple user lookup using GET
            with httpx.Client() as client:
                response = client.get(
                    f"{self.api_base_url}/user",
                    headers=headers,
                    params={"username": "twitter"},
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    return True
                else:
                    print(f"⚠ RapidAPI test failed: {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                    return False
                    
        except Exception as e:
            print(f"⚠ RapidAPI connection test error: {e}")
            return False
    
    def fetch_tweets_from_handle(self, handle: str, max_results: int = 10) -> List[Dict]:
        """
        Fetch tweets from a specific Twitter handle using RapidAPI (twitter241).
        
        Args:
            handle: Twitter handle (without @)
            max_results: Maximum number of tweets to fetch
            
        Returns:
            List of tweet dictionaries
        """
        # If in mock mode, always return mock data
        if self.use_mock_data:
            return self._generate_mock_tweets(handle, max_results)
        
        # If API is enabled, try to fetch real tweets
        # Don't fall back to mock data - return empty list on failure
        try:
            headers = self._get_rapidapi_headers()
            
            with httpx.Client() as client:
                # Step 1: Get user information using GET
                print(f"🔍 Looking up user: @{handle}")
                user_response = client.get(
                    f"{self.api_base_url}/user",
                    headers=headers,
                    params={"username": handle},
                    timeout=15.0
                )
                
                if user_response.status_code != 200:
                    print(f"⚠ Failed to get user {handle}: {user_response.status_code}")
                    print(f"Response: {user_response.text[:200]}")
                    return []  # Return empty, don't generate mock data
                
                user_data = user_response.json()
                
                # Debug: Print response structure
                print(f"📋 User API response keys: {list(user_data.keys())}")
                
                # Check if user exists (empty data means user not found)
                if "result" in user_data and "data" in user_data["result"]:
                    if not user_data["result"]["data"] or user_data["result"]["data"] == {}:
                        print(f"⚠ User @{handle} does not exist on Twitter")
                        print(f"💡 Tip: Use real Twitter accounts like 'twitter', 'NASA', 'elonmusk'")
                        return []  # Return empty, don't generate mock data
                
                # Extract user info from twitter241 response
                # Try different possible response structures
                user_info = None
                user_id = None
                user_name = None
                
                # Structure 1: result.data.user.result
                if "result" in user_data and "data" in user_data.get("result", {}):
                    data = user_data["result"]["data"]
                    if "user" in data and "result" in data.get("user", {}):
                        user_info = data["user"]["result"]
                        user_id = user_info.get("rest_id")
                        user_name = user_info.get("legacy", {}).get("name", handle.title())
                
                # Structure 2: Direct user object
                elif "user" in user_data:
                    user_info = user_data["user"]
                    user_id = user_info.get("id_str") or user_info.get("rest_id")
                    user_name = user_info.get("name", handle.title())
                
                # Structure 3: Direct fields
                elif "id_str" in user_data or "rest_id" in user_data:
                    user_id = user_data.get("id_str") or user_data.get("rest_id")
                    user_name = user_data.get("name", handle.title())
                
                if not user_id:
                    print(f"⚠ Could not extract user ID from response")
                    print(f"Response structure: {str(user_data)[:300]}...")
                    return []  # Return empty, don't generate mock data
                
                print(f"✓ Found user: {user_name} (ID: {user_id})")
                
                # Step 2: Get user's tweets using GET
                print(f"📥 Fetching tweets from @{handle}...")
                tweets_response = client.get(
                    f"{self.api_base_url}/user-tweets",
                    headers=headers,
                    params={
                        "user": user_id,
                        "count": str(min(max_results, 40))
                    },
                    timeout=15.0
                )
                
                if tweets_response.status_code == 429:
                    print(f"⚠ Rate limit exceeded for {handle}")
                    return []  # Return empty, don't generate mock data
                
                if tweets_response.status_code != 200:
                    print(f"⚠ Failed to get tweets for {handle}: {tweets_response.status_code}")
                    print(f"Response: {tweets_response.text[:200]}")
                    return []  # Return empty, don't generate mock data
                
                tweets_data = tweets_response.json()
                
                # Debug: Print tweets response structure
                print(f"📋 Tweets API response keys: {list(tweets_data.keys())}")
                if "result" in tweets_data:
                    result = tweets_data["result"]
                    print(f"📋 Result keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
                    if isinstance(result, dict) and "timeline" in result:
                        timeline = result["timeline"]
                        print(f"📋 Timeline keys: {list(timeline.keys()) if isinstance(timeline, dict) else 'not a dict'}")
                
                # Parse twitter241 response structure
                # Handle different response formats
                instructions = []
                
                # Format 1: result.timeline.instructions (most common)
                if "result" in tweets_data and isinstance(tweets_data["result"], dict):
                    timeline = tweets_data["result"].get("timeline", {})
                    if isinstance(timeline, dict):
                        instructions = timeline.get("instructions", [])
                        print(f"📋 Found {len(instructions)} instructions in timeline")
                
                # Format 2: data.user (alternate format)
                elif "data" in tweets_data:
                    print(f"⚠ Alternate response format with 'data' key")
                    print(f"Response preview: {str(tweets_data)[:500]}...")
                    return []
                
                if not instructions:
                    print(f"⚠ No instructions found in tweets response")
                    return []
                
                parsed_tweets = []
                for instruction in instructions:
                    if instruction.get("type") == "TimelineAddEntries":
                        entries = instruction.get("entries", [])
                        
                        for entry in entries:
                            if "tweet-" in entry.get("entryId", ""):
                                try:
                                    content = entry.get("content", {})
                                    item_content = content.get("itemContent", {})
                                    tweet_results = item_content.get("tweet_results", {})
                                    result = tweet_results.get("result", {})
                                    
                                    if result.get("__typename") == "Tweet":
                                        legacy = result.get("legacy", {})
                                        
                                        tweet_id = legacy.get("id_str") or result.get("rest_id")
                                        tweet_text = legacy.get("full_text", "")
                                        created_at_str = legacy.get("created_at", "")
                                        
                                        # Parse Twitter's date format
                                        try:
                                            created_at = datetime.strptime(created_at_str, "%a %b %d %H:%M:%S %z %Y")
                                        except:
                                            created_at = datetime.now()
                                        
                                        # Skip retweets
                                        if not tweet_text.startswith("RT @"):
                                            tweet_data = {
                                                'tweet_id': str(tweet_id),
                                                'text': tweet_text,
                                                'author_handle': handle,
                                                'author_name': user_name,
                                                'created_at_twitter': created_at,
                                                'media_url': None,
                                                'tweet_url': f"https://twitter.com/{handle}/status/{tweet_id}"
                                            }
                                            parsed_tweets.append(tweet_data)
                                            
                                            if len(parsed_tweets) >= max_results:
                                                break
                                except Exception as e:
                                    print(f"⚠ Error parsing tweet entry: {e}")
                                    continue
                
                if parsed_tweets:
                    print(f"✓ Fetched {len(parsed_tweets)} tweets from @{handle}")
                    return parsed_tweets
                else:
                    print(f"⚠ No tweets found for {handle}")
                    return []  # Return empty, don't generate mock data
                
        except httpx.TimeoutException:
            print(f"⚠ Timeout fetching tweets for {handle}")
            return []  # Return empty, don't generate mock data
        except Exception as e:
            print(f"⚠ Error fetching tweets for {handle}: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return []  # Return empty, don't generate mock data
    
    def _generate_mock_tweets(self, handle: str, count: int = 10) -> List[Dict]:
        """
        Generate mock tweets for testing and fallback.
        
        Args:
            handle: Twitter handle
            count: Number of mock tweets to generate
            
        Returns:
            List of mock tweet dictionaries
        """
        mock_texts = [
            "Just shipped a major update to our platform! 🚀 Excited to see what you all build with it.",
            "Thinking about the future of AI and how it will transform software development.",
            "Coffee + Code = Productivity ☕💻 #DevLife",
            "Pro tip: Always write tests before you think you need them. Future you will thank present you.",
            "The best code is no code at all. Sometimes the solution is simpler than you think.",
            "Debugging is like being a detective in a crime movie where you're also the murderer.",
            "Just discovered an amazing new library that solves a problem I've been wrestling with for weeks!",
            "Remember: premature optimization is the root of all evil. Make it work, then make it fast.",
            "Collaboration > Competition. The best projects come from teams that support each other.",
            "Taking a break from coding to recharge. Sometimes the best solutions come when you step away.",
            "Open source is amazing. Shoutout to all the maintainers who make our lives easier! 🙏",
            "Learning a new programming language is like learning to think in a different way.",
            "Code review isn't about finding mistakes, it's about sharing knowledge and improving together.",
            "The documentation you write today saves hours of confusion tomorrow.",
            "Refactoring old code and finding comments from past me. It's like time travel! 😄"
        ]
        
        tweets = []
        base_time = datetime.now()
        
        for i in range(count):
            # Generate unique tweet ID
            tweet_id = f"mock_{handle}_{int(datetime.now().timestamp())}_{i}_{random.randint(1000, 9999)}"
            
            # Random tweet text
            text = random.choice(mock_texts)
            
            # Timestamp (going back in time)
            created_at = base_time - timedelta(hours=i * 2, minutes=random.randint(0, 59))
            
            tweet_data = {
                'tweet_id': tweet_id,
                'text': text,
                'author_handle': handle,
                'author_name': handle.title(),
                'created_at_twitter': created_at,
                'media_url': None,
                'tweet_url': f"https://twitter.com/{handle}/status/{tweet_id}"
            }
            tweets.append(tweet_data)
        
        return tweets
    
    def fetch_and_store_tweets(self, db: Session) -> Dict[str, int]:
        """
        Fetch tweets from all active handles and store in database.
        Implements deduplication logic.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with statistics (fetched, new, duplicates)
        """
        stats = {
            'fetched': 0,
            'new': 0,
            'duplicates': 0,
            'handles_processed': 0
        }
        
        # Get all active Twitter handles
        active_handles = db.query(TwitterHandle).filter(TwitterHandle.is_active == True).all()
        
        if not active_handles:
            print("No active Twitter handles found")
            return stats
        
        for handle_obj in active_handles:
            handle = handle_obj.handle
            print(f"Fetching tweets for @{handle}...")
            
            # Fetch tweets
            tweets = self.fetch_tweets_from_handle(handle, max_results=10)
            stats['fetched'] += len(tweets)
            stats['handles_processed'] += 1
            
            # Store tweets with deduplication
            for tweet_data in tweets:
                # Check if tweet already exists
                existing_tweet = db.query(Tweet).filter(
                    Tweet.tweet_id == tweet_data['tweet_id']
                ).first()
                
                if existing_tweet:
                    stats['duplicates'] += 1
                    continue
                
                # Create new tweet
                new_tweet = Tweet(
                    tweet_id=tweet_data['tweet_id'],
                    text=tweet_data['text'],
                    author_handle=tweet_data['author_handle'],
                    author_name=tweet_data['author_name'],
                    created_at_twitter=tweet_data['created_at_twitter'],
                    media_url=tweet_data['media_url'],
                    tweet_url=tweet_data['tweet_url'],
                    is_displayed=False
                )
                
                db.add(new_tweet)
                stats['new'] += 1
            
            # Commit after each handle
            try:
                db.commit()
            except Exception as e:
                print(f"Error storing tweets for {handle}: {e}")
                db.rollback()
        
        print(f"Fetch complete: {stats}")
        return stats
    
    def get_next_undisplayed_tweet(self, db: Session) -> Optional[Tweet]:
        """
        Get the next tweet that hasn't been displayed.
        
        Args:
            db: Database session
            
        Returns:
            Tweet object or None
        """
        tweet = db.query(Tweet).filter(
            Tweet.is_displayed == False
        ).order_by(
            Tweet.created_at_twitter.desc()
        ).first()
        
        return tweet
    
    def mark_tweet_as_displayed(self, db: Session, tweet_id: str) -> bool:
        """
        Mark a tweet as displayed and add to displayed_tweets table.
        
        Args:
            db: Database session
            tweet_id: Tweet ID to mark
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get tweet
            tweet = db.query(Tweet).filter(Tweet.tweet_id == tweet_id).first()
            if not tweet:
                print(f"Tweet {tweet_id} not found")
                return False
            
            # Check if already marked as displayed
            existing_displayed = db.query(DisplayedTweet).filter(
                DisplayedTweet.tweet_id == tweet_id
            ).first()
            
            if existing_displayed:
                print(f"Tweet {tweet_id} already marked as displayed")
                return True  # Return True since it's already in the desired state
            
            # Update tweet
            tweet.is_displayed = True
            tweet.displayed_at = datetime.now()
            
            # Add to displayed_tweets table
            displayed_tweet = DisplayedTweet(tweet_id=tweet_id)
            db.add(displayed_tweet)
            
            db.commit()
            print(f"Successfully marked tweet {tweet_id} as displayed")
            return True
            
        except Exception as e:
            print(f"Error marking tweet as displayed: {e}")
            db.rollback()
            return False
    
    def get_stats(self, db: Session) -> Dict[str, int]:
        """
        Get statistics about tweets.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with statistics
        """
        total_tweets = db.query(Tweet).count()
        displayed_tweets = db.query(Tweet).filter(Tweet.is_displayed == True).count()
        remaining_tweets = total_tweets - displayed_tweets
        active_handles = db.query(TwitterHandle).filter(TwitterHandle.is_active == True).count()
        
        return {
            'total_tweets': total_tweets,
            'displayed_tweets': displayed_tweets,
            'remaining_tweets': remaining_tweets,
            'active_handles': active_handles
        }
