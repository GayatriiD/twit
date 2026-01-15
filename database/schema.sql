-- Twitter Feed Display System - Database Schema
-- PostgreSQL 12+

-- Drop existing tables if they exist
DROP TABLE IF EXISTS displayed_tweets CASCADE;
DROP TABLE IF EXISTS tweets CASCADE;
DROP TABLE IF EXISTS twitter_handles CASCADE;

-- Twitter handles configuration table
CREATE TABLE twitter_handles (
    id SERIAL PRIMARY KEY,
    handle VARCHAR(255) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tweets table - stores all fetched tweets
CREATE TABLE tweets (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(255) NOT NULL UNIQUE,
    text TEXT NOT NULL,
    author_handle VARCHAR(255) NOT NULL,
    author_name VARCHAR(255),
    created_at_twitter TIMESTAMP NOT NULL,
    media_url TEXT,
    tweet_url TEXT NOT NULL,
    is_displayed BOOLEAN DEFAULT FALSE,
    displayed_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Displayed tweets tracking table - for persistent deduplication
CREATE TABLE displayed_tweets (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(255) NOT NULL UNIQUE REFERENCES tweets(tweet_id) ON DELETE CASCADE,
    displayed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_tweets_tweet_id ON tweets(tweet_id);
CREATE INDEX idx_tweets_is_displayed ON tweets(is_displayed);
CREATE INDEX idx_tweets_author_handle ON tweets(author_handle);
CREATE INDEX idx_tweets_fetched_at ON tweets(fetched_at DESC);
CREATE INDEX idx_tweets_display_status ON tweets(is_displayed, fetched_at DESC);
CREATE INDEX idx_displayed_tweets_tweet_id ON displayed_tweets(tweet_id);
CREATE INDEX idx_twitter_handles_active ON twitter_handles(is_active);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for twitter_handles updated_at
CREATE TRIGGER update_twitter_handles_updated_at
    BEFORE UPDATE ON twitter_handles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some default Twitter handles for testing
INSERT INTO twitter_handles (handle, is_active) VALUES
    ('elonmusk', TRUE),
    ('BillGates', TRUE),
    ('naval', TRUE)
ON CONFLICT (handle) DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE twitter_handles IS 'Configuration table for Twitter accounts to monitor';
COMMENT ON TABLE tweets IS 'All fetched tweets with metadata';
COMMENT ON TABLE displayed_tweets IS 'Audit log of displayed tweets for deduplication';
COMMENT ON COLUMN tweets.is_displayed IS 'Flag indicating if tweet has been displayed';
COMMENT ON COLUMN tweets.tweet_id IS 'Twitter unique tweet identifier';
