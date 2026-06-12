import requests
from typing import List, Dict, Any

class RiigikoguClient:
    BASE_URL = "https://api.riigikogu.ee"
    HEADERS = {
        "Accept": "application/json",
        "User-Agent": "Estonia-Civic-Analytics-Bot/1.0"
    }

    def get_collective_addresses(self) -> List[Dict[str, Any]]:
        """Fetch all collective addresses (petitions) from Riigikogu."""
        url = f"{self.BASE_URL}/api/documents/collective-addresses"
        response = requests.get(url, headers=self.HEADERS)
        response.raise_for_status()
        return response.json()

    def get_draft_details(self, draft_uuid: str) -> Dict[str, Any]:
        """Fetch detailed information about a draft bill (eelnõu)."""
        url = f"{self.BASE_URL}/api/volumes/drafts/{draft_uuid}"
        response = requests.get(url, headers=self.HEADERS)
        response.raise_for_status()
        return response.json()

    def get_voting_details(self, voting_uuid: str) -> Dict[str, Any]:
        """Fetch detailed vote results for a specific voting."""
        url = f"{self.BASE_URL}/api/votings/{voting_uuid}"
        response = requests.get(url, headers=self.HEADERS)
        response.raise_for_status()
        return response.json()
