"""Discovery Agent: Interacts with the browser to fetch DOM, styles, and screenshots."""
from typing import Dict, Any
from backend.app.browser.service import BrowserService


class DiscoveryAgent:
    def __init__(self, browser_service: BrowserService = None):
        self.browser_service = browser_service or BrowserService()

    async def run(self, url: str, project_id: str) -> Dict[str, Any]:
        """Execute discovery workflow on the target website."""
        raw_discovery = await self.browser_service.capture_website(url, project_id)
        return raw_discovery
