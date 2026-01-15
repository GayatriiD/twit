"""SQLAlchemy ORM models for the Twitter Feed Display System."""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class TwitterHandle(Base):
    """Model for Twitter handles configuration."""
    __tablename__ = "twitter_handles"
    
    id = Column(Integer, primary_key=True, index=True)
    handle = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "handle": self.handle,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Tweet(Base):
    """Model for tweets."""
    __tablename__ = "tweets"
    
    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String(255), unique=True, nullable=False, index=True)
    text = Column(Text, nullable=False)
    author_handle = Column(String(255), nullable=False, index=True)
    author_name = Column(String(255))
    created_at_twitter = Column(DateTime(timezone=True), nullable=False)
    media_url = Column(Text)
    tweet_url = Column(Text, nullable=False)
    is_displayed = Column(Boolean, default=False, index=True)
    displayed_at = Column(DateTime(timezone=True))
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "tweet_id": self.tweet_id,
            "text": self.text,
            "author_handle": self.author_handle,
            "author_name": self.author_name,
            "created_at_twitter": self.created_at_twitter.isoformat() if self.created_at_twitter else None,
            "media_url": self.media_url,
            "tweet_url": self.tweet_url,
            "is_displayed": self.is_displayed,
            "displayed_at": self.displayed_at.isoformat() if self.displayed_at else None,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None
        }

class DisplayedTweet(Base):
    """Model for tracking displayed tweets (deduplication)."""
    __tablename__ = "displayed_tweets"
    
    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String(255), ForeignKey("tweets.tweet_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    displayed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "tweet_id": self.tweet_id,
            "displayed_at": self.displayed_at.isoformat() if self.displayed_at else None
        }
