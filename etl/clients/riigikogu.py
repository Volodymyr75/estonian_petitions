import requests
from typing import List, Dict, Any
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

class RiigikoguClient:
    BASE_URL = "https://api.riigikogu.ee"
    HEADERS = {
        "Accept": "application/json",
        "User-Agent": "Estonia-Civic-Analytics-Bot/1.0"
    }
    TIMEOUT = 15  # 15 seconds timeout

    def __init__(self):
        self.session = requests.Session()
        # Retry connect & read timeouts, as well as common server errors (500, 502, 503, 504)
        # up to 3 times, with exponential backoff (1s, 2s, 4s)
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get_collective_addresses(self) -> List[Dict[str, Any]]:
        """Fetch all collective addresses (petitions) from Riigikogu."""
        url = f"{self.BASE_URL}/api/documents/collective-addresses"
        response = self.session.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.json()

    def get_draft_details(self, draft_uuid: str) -> Dict[str, Any]:
        """Fetch detailed information about a draft bill (eelnõu)."""
        url = f"{self.BASE_URL}/api/volumes/drafts/{draft_uuid}"
        response = self.session.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.json()

    def get_voting_details(self, voting_uuid: str) -> Dict[str, Any]:
        """Fetch detailed vote results for a specific voting."""
        url = f"{self.BASE_URL}/api/votings/{voting_uuid}"
        response = self.session.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.json()
