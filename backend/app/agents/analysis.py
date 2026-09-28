"""Analysis Agent: Synthesizes DOM, computed styles, and visual screenshots."""
from typing import Dict, Any
from backend.app.services.llm_provider import LLMProvider


class AnalysisAgent:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def run(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process discovery data and visual metrics into a refined architectural analysis."""
        dom_summary = {
            "title": discovery_data.get("title", ""),
            "description": discovery_data.get("description", ""),
            "brandName": discovery_data.get("brandName", ""),
            "colors": discovery_data.get("colors", {}),
            "fontFamily": discovery_data.get("fontFamily", "Inter, sans-serif"),
            "headings": discovery_data.get("headings", []),
            "buttons": discovery_data.get("buttons", []),
            "navigation": discovery_data.get("navigation", {}),
        }

        visual_summary = {
            "desktop_screenshot": discovery_data.get("desktop_screenshot"),
            "mobile_screenshot": discovery_data.get("mobile_screenshot"),
            "layout_type": "modern-landing",
            "detected_sections_count": len(discovery_data.get("sections", [])),
        }

        # Analyze using LLM (or fallback heuristic engine)
        llm_analysis = await self.llm.analyze(dom_summary, visual_summary)

        # Merge with high-accuracy discovery extraction
        theme = llm_analysis.get("theme", {})
        if not theme.get("primaryColor") or theme.get("primaryColor") == "#2563eb":
            theme["primaryColor"] = discovery_data.get("colors", {}).get("primary", "#2563eb")
        if not theme.get("backgroundColor"):
            theme["backgroundColor"] = discovery_data.get("colors", {}).get("background", "#ffffff")
        if not theme.get("textColor"):
            theme["textColor"] = discovery_data.get("colors", {}).get("text", "#0f172a")

        return {
            "title": discovery_data.get("title", "Replicate.AI App"),
            "description": discovery_data.get("description", ""),
            "brandName": discovery_data.get("brandName", "Brand"),
            "theme": theme,
            "navigation": discovery_data.get("navigation", {}),
            "sections": discovery_data.get("sections", []),
            "images": discovery_data.get("images", []),
            "desktop_screenshot": discovery_data.get("desktop_screenshot"),
            "mobile_screenshot": discovery_data.get("mobile_screenshot"),
            "fontFamily": discovery_data.get("fontFamily", "Inter, sans-serif"),
        }
