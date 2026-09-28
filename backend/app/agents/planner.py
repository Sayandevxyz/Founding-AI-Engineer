"""UI Planning Agent: Formulates the WebsiteSpec IR contract from analysis and assets."""
from typing import Dict, Any
from backend.app.schemas.website_spec import (
    WebsiteSpec,
    ThemeSpec,
    NavigationSpec,
    NavigationItem,
    NavigationCTA,
    SectionSpec,
    ComponentSpec,
    AssetManifest,
    ImageSpec,
)
from backend.app.services.llm_provider import LLMProvider


class PlannerAgent:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def run(
        self,
        url: str,
        analysis_data: Dict[str, Any],
        asset_manifest: AssetManifest
    ) -> WebsiteSpec:
        """Create a validated WebsiteSpec IR."""
        # Query LLM (or heuristic planner)
        plan_spec = await self.llm.plan(analysis_data, url)

        # Merge concrete asset mapping
        plan_spec.assets = asset_manifest.assets

        # Map assets to hero and sections
        if asset_manifest.assets:
            for sec in plan_spec.sections:
                if sec.type == "hero" and not sec.images:
                    first_asset = asset_manifest.assets[0]
                    sec.images = [ImageSpec(
                        url=first_asset.sourceUrl,
                        localPath=first_asset.localPath,
                        alt=first_asset.alt or "Hero Visual",
                        role="hero",
                    )]

        # Ensure components tree is explicitly cataloged
        plan_spec.components = [
            ComponentSpec(
                name="Navbar",
                file="src/components/Navbar.tsx",
                description="Responsive top navigation bar with brand logo, nav links, and CTA",
            ),
            ComponentSpec(
                name="Hero",
                file="src/components/Hero.tsx",
                description="High-impact hero section with value proposition, call-to-action buttons, and visual showcase",
            ),
            ComponentSpec(
                name="Features",
                file="src/components/Features.tsx",
                description="Feature showcase grid highlighting core value pillars with icons and descriptions",
            ),
            ComponentSpec(
                name="Testimonials",
                file="src/components/Testimonials.tsx",
                description="Social proof and testimonial cards with user ratings and company affiliations",
            ),
            ComponentSpec(
                name="CTA",
                file="src/components/CTA.tsx",
                description="High-conversion call-to-action banner driving signups or demos",
            ),
            ComponentSpec(
                name="Footer",
                file="src/components/Footer.tsx",
                description="Site footer with multi-column links, copyright, and social links",
            ),
        ]

        plan_spec.responsiveRules = [
            "Mobile (<768px): Navigation collapses to clean mobile menu; multi-column grids collapse to single-column stack",
            "Tablet (768px-1024px): 2-column grid arrangements; adjusted heading font sizes",
            "Desktop (>1024px): Full layout with sticky glassmorphism header, 3-column feature cards, and 4-column footer",
        ]

        # Design tokens
        plan_spec.designTokens = {
            "colors": {
                "primary": plan_spec.theme.primaryColor,
                "secondary": plan_spec.theme.secondaryColor,
                "accent": plan_spec.theme.accentColor,
                "background": plan_spec.theme.backgroundColor,
                "text": plan_spec.theme.textColor,
            },
            "typography": {
                "fontFamily": plan_spec.theme.fontFamily,
                "headingFont": plan_spec.theme.headingFont,
            },
            "radii": {
                "default": plan_spec.theme.borderRadius,
            },
        }

        return plan_spec
