import requests
from typing import List, Dict, Any

class RahvaalgatusClient:
    BASE_URL = "https://rahvaalgatus.ee"
    HEADERS = {
        "Accept": "application/vnd.rahvaalgatus.initiative+json; v=1",
        "User-Agent": "Estonia-Civic-Analytics-Bot/1.0"
    }

    def get_initiatives(self, limit: int = None) -> List[Dict[str, Any]]:
        """Fetch the list of initiatives."""
        url = f"{self.BASE_URL}/initiatives"
        response = requests.get(url, headers=self.HEADERS)
        response.raise_for_status()
        data = response.json()
        if limit:
            return data[:limit]
        return data

    def get_initiative_details(self, initiative_id: str) -> Dict[str, Any]:
        """Fetch details of a single initiative."""
        url = f"{self.BASE_URL}/initiatives/{initiative_id}"
        response = requests.get(url, headers=self.HEADERS)
        response.raise_for_status()
        return response.json()

    def get_events(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Fetch initiative events."""
        url = f"{self.BASE_URL}/initiative-events?limit={limit}"
        headers = self.HEADERS.copy()
        headers["Accept"] = "application/vnd.rahvaalgatus.initiative-event+json; v=1"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
