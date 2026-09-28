"""Strict Pydantic Schema for WebsiteSpec Intermediate Representation (IR)."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ViewportDimensions(BaseModel):
    width: int
    height: int


class ViewportSpec(BaseModel):
    desktop: ViewportDimensions = Field(default_factory=lambda: ViewportDimensions(width=1440, height=900))
    tablet: ViewportDimensions = Field(default_factory=lambda: ViewportDimensions(width=768, height=1024))
    mobile: ViewportDimensions = Field(default_factory=lambda: ViewportDimensions(width=390, height=844))


class ThemeSpec(BaseModel):
    primaryColor: str = "#2563eb"
    secondaryColor: str = "#4f46e5"
    accentColor: str = "#06b6d4"
    backgroundColor: str = "#ffffff"
    surfaceColor: str = "#f8fafc"
    textColor: str = "#0f172a"
    mutedTextColor: str = "#64748b"
    fontFamily: str = "Inter, sans-serif"
    headingFont: str = "Inter, sans-serif"
    borderRadius: str = "0.5rem"
    shadows: str = "0 4px 6px -1px rgb(0 0 0 / 0.1)"
    isDark: bool = False


class NavigationItem(BaseModel):
    label: str
    href: str = "#"
    isExternal: bool = False


class NavigationCTA(BaseModel):
    label: str
    href: str = "#"
    variant: str = "primary"


class NavigationSpec(BaseModel):
    logo: Optional[str] = None
    brandName: Optional[str] = "Brand"
    items: List[NavigationItem] = Field(default_factory=list)
    cta: Optional[NavigationCTA] = None
    isSticky: bool = True


class ButtonSpec(BaseModel):
    label: str
    variant: str = "primary"  # primary, secondary, outline, ghost
    href: str = "#"


class ImageSpec(BaseModel):
    url: str
    localPath: Optional[str] = None
    alt: Optional[str] = ""
    role: Optional[str] = "illustration"  # hero, illustration, icon, avatar, background
    width: Optional[int] = None
    height: Optional[int] = None


class SectionItem(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    image: Optional[str] = None
    price: Optional[str] = None
    period: Optional[str] = None
    badge: Optional[str] = None
    author: Optional[str] = None
    role: Optional[str] = None
    rating: Optional[float] = None
    features: List[str] = Field(default_factory=list)
    button: Optional[ButtonSpec] = None


class SectionSpec(BaseModel):
    id: str
    type: str  # hero, features, testimonials, pricing, cta, faq, stats, footer, logos, gallery
    order: int
    heading: Optional[str] = None
    subheading: Optional[str] = None
    badge: Optional[str] = None
    content: Optional[str] = None
    buttons: List[ButtonSpec] = Field(default_factory=list)
    images: List[ImageSpec] = Field(default_factory=list)
    layout: str = "centered"  # centered, split, 2-column, 3-column-grid, 4-column-grid, stack
    responsiveBehavior: str = "stack-on-mobile"
    items: List[SectionItem] = Field(default_factory=list)


class AssetManifestItem(BaseModel):
    id: str
    sourceUrl: str
    localPath: str
    type: str = "image"  # image, svg, icon, font
    width: Optional[int] = None
    height: Optional[int] = None
    alt: Optional[str] = ""
    status: str = "downloaded"  # downloaded, placeholder, failed


class AssetManifest(BaseModel):
    assets: List[AssetManifestItem] = Field(default_factory=list)


class ComponentSpec(BaseModel):
    name: str
    file: str
    description: str
    props: Dict[str, Any] = Field(default_factory=dict)
    imports: List[str] = Field(default_factory=list)


class WebsiteSpec(BaseModel):
    url: str
    title: str = "Reconstructed Website"
    description: Optional[str] = ""
    viewport: ViewportSpec = Field(default_factory=ViewportSpec)
    theme: ThemeSpec = Field(default_factory=ThemeSpec)
    navigation: NavigationSpec = Field(default_factory=NavigationSpec)
    sections: List[SectionSpec] = Field(default_factory=list)
    assets: List[AssetManifestItem] = Field(default_factory=list)
    components: List[ComponentSpec] = Field(default_factory=list)
    responsiveRules: List[str] = Field(default_factory=list)
    designTokens: Dict[str, Any] = Field(default_factory=dict)
