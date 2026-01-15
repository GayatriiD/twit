"""Database initialization script."""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base, check_db_connection
from models import TwitterHandle, Tweet, DisplayedTweet

def init_database():
    """Initialize database tables."""
    print("Initializing database...")
    
    # Check connection
    if not check_db_connection():
        print("ERROR: Cannot connect to database!")
        print("Please ensure PostgreSQL is running and DATABASE_URL is correct in .env")
        return False
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully!")
        
        # Print created tables
        print("\nCreated tables:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create tables: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
