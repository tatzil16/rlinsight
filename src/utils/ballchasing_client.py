# src/utils/ballchasing_client.py
import requests
from typing import Optional, Dict, List
import os
import time
from requests.exceptions import HTTPError


class BallchasingClient:
    """Client for interacting with the Ballchasing API."""
    
    BASE_URL = "https://ballchasing.com/api"
    
    def __init__(self, api_key: str):
        """
        Initialize the Ballchasing client.
        
        Args:
            api_key: Your Ballchasing API token
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": api_key
        })
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum seconds between requests
    
    def _rate_limit_wait(self):
        """Wait if necessary to respect rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            wait_time = self.min_request_interval - elapsed
            print(f"⏳ Rate limiting: waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Optional[Dict] = None, max_retries: int = 3):
        """
        Make a request with rate limiting and retry logic.
        
        Args:
            url: Full URL to request
            params: Query parameters
            max_retries: Number of times to retry on 429 errors
            
        Returns:
            Response JSON
        """
        for attempt in range(max_retries):
            self._rate_limit_wait()
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                return response.json()
                
            except HTTPError as e:
                if e.response.status_code == 429:  # Rate limit error
                    wait_time = 60 * (attempt + 1)  # Wait 60s, 120s, 180s...
                    print(f"⚠️  Rate limit hit. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                else:
                    raise  # Re-raise other HTTP errors
        
        raise HTTPError("Max retries exceeded due to rate limiting")
    
    def get_replays(self, 
                    uploader: Optional[str] = None,
                    count: int = 10,
                    sort_by: str = "replay-date",
                    sort_dir: str = "desc") -> List[Dict]:
        """
        Fetch a list of replays.
        
        Args:
            uploader: Steam ID or 'me' to filter by uploader
            count: Number of replays to fetch (max 200)
            sort_by: Field to sort by (replay-date, upload-date, etc.)
            sort_dir: Sort direction (asc or desc)
            
        Returns:
            List of replay metadata dictionaries
        """
        params = {
            "count": count,
            "sort-by": sort_by,
            "sort-dir": sort_dir
        }
        
        if uploader:
            params["uploader"] = uploader
        
        data = self._make_request(f"{self.BASE_URL}/replays", params=params)
        return data.get("list", [])
    
    def get_replay_details(self, replay_id: str) -> Dict:
        """
        Get detailed stats for a specific replay.
        
        Args:
            replay_id: The replay ID
            
        Returns:
            Dictionary with full replay data including player stats
        """
        return self._make_request(f"{self.BASE_URL}/replays/{replay_id}")


# Helper function to create client from environment
def create_client() -> BallchasingClient:
    """Create a Ballchasing client using the API key from environment."""
    api_key = os.getenv("BALLCHASING_API_KEY")
    if not api_key:
        raise ValueError("BALLCHASING_API_KEY not found in environment")
    return BallchasingClient(api_key)