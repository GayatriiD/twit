"""Test script to verify RapidAPI Twitter connection."""

import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_rapidapi():
    """Test RapidAPI connection with detailed output."""
    
    print("=" * 60)
    print("RapidAPI Twitter Connection Test")
    print("=" * 60)
    
    # Check if API key exists
    rapidapi_key = os.getenv("RAPIDAPI_KEY")
    
    if not rapidapi_key:
        print("❌ RAPIDAPI_KEY not found in .env file!")
        print("\nPlease add to your .env file:")
        print("RAPIDAPI_KEY=your_actual_key_here")
        return False
    
    print(f"✓ RAPIDAPI_KEY found (length: {len(rapidapi_key)})")
    print(f"  First 10 chars: {rapidapi_key[:10]}...")
    print()
    
    # Test with twitter-api49
    rapidapi_host = "twitter-api49.p.rapidapi.com"
    
    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": rapidapi_host
    }
    
    print(f"Testing API: {rapidapi_host}")
    print()
    
    # Test 1: User lookup
    print("Test 1: Looking up user 'twitter'...")
    try:
        with httpx.Client() as client:
            response = client.get(
                f"https://{rapidapi_host}/user/details",
                headers=headers,
                params={"username": "twitter"},
                timeout=15.0
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ SUCCESS! API is working")
                data = response.json()
                print(f"Response preview: {str(data)[:200]}...")
                return True
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
                # Common error messages
                if response.status_code == 401:
                    print("\n💡 This usually means:")
                    print("   - Invalid API key")
                    print("   - API key not activated")
                elif response.status_code == 403:
                    print("\n💡 This usually means:")
                    print("   - Not subscribed to this API")
                    print("   - Subscription expired")
                elif response.status_code == 429:
                    print("\n💡 This usually means:")
                    print("   - Rate limit exceeded")
                    print("   - Wait and try again")
                
                return False
                
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_rapidapi()
    print()
    print("=" * 60)
    if success:
        print("✅ RapidAPI is configured correctly!")
        print("\nYou can now set USE_MOCK_DATA=false in .env")
    else:
        print("❌ RapidAPI is not working")
        print("\nSteps to fix:")
        print("1. Get API key from https://rapidapi.com/")
        print("2. Subscribe to 'Twitter API v2' or similar")
        print("3. Add RAPIDAPI_KEY to .env file")
        print("4. Run this test again")
    print("=" * 60)
