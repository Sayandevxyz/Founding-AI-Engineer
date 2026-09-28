"""Asset Agent: Safely extracts, downloads, and manages media assets with crisp fallback placeholders."""
import os
import re
import httpx
from typing import List, Dict, Any
from urllib.parse import urlparse
from backend.app.schemas.website_spec import AssetManifest, AssetManifestItem


class AssetAgent:
    def __init__(self, timeout_secs: float = 8.0, max_assets: int = 15):
        self.timeout_secs = timeout_secs
        self.max_assets = max_assets

    async def process_assets(
        self,
        raw_images: List[Dict[str, str]],
        project_dir: str,
        base_url: str
    ) -> AssetManifest:
        """
        Download images and assets into project's public/assets directory.
        Generate vector placeholders for blocked/failed assets.
        """
        assets_dir = os.path.join(project_dir, "public", "assets")
        os.makedirs(assets_dir, exist_ok=True)

        manifest_items: List[AssetManifestItem] = []

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }

        async with httpx.AsyncClient(timeout=self.timeout_secs, follow_redirects=True) as client:
            for idx, img in enumerate(raw_images[:self.max_assets]):
                src = img.get("url", "")
                alt = img.get("alt", "") or f"Asset {idx + 1}"
                if not src:
                    continue

                asset_id = f"asset-{idx + 1}"
                ext = self._guess_extension(src)
                filename = f"{asset_id}{ext}"
                local_fs_path = os.path.join(assets_dir, filename)
                public_web_path = f"/assets/{filename}"

                downloaded = False
                try:
                    res = await client.get(src, headers=headers)
                    if res.status_code == 200 and len(res.content) > 100:
                        # Limit individual asset size to 5MB to control costs/storage
                        if len(res.content) <= 5 * 1024 * 1024:
                            with open(local_fs_path, "wb") as f:
                                f.write(res.content)
                            downloaded = True
                except Exception:
                    downloaded = False

                if not downloaded:
                    # Generate an SVG placeholder
                    filename = f"{asset_id}.svg"
                    local_fs_path = os.path.join(assets_dir, filename)
                    public_web_path = f"/assets/{filename}"
                    self._create_svg_placeholder(local_fs_path, alt, width=800, height=500)
                    manifest_items.append(
                        AssetManifestItem(
                            id=asset_id,
                            sourceUrl=src,
                            localPath=public_web_path,
                            type="svg",
                            alt=alt,
                            status="placeholder",
                        )
                    )
                else:
                    manifest_items.append(
                        AssetManifestItem(
                            id=asset_id,
                            sourceUrl=src,
                            localPath=public_web_path,
                            type="image" if ext != ".svg" else "svg",
                            alt=alt,
                            status="downloaded",
                        )
                    )

        # Ensure we at least have a default hero visual asset
        if not manifest_items:
            hero_path = os.path.join(assets_dir, "hero-visual.svg")
            self._create_svg_placeholder(hero_path, "Hero Showcase Visual", 1200, 700)
            manifest_items.append(
                AssetManifestItem(
                    id="hero-visual",
                    sourceUrl="generated://placeholder",
                    localPath="/assets/hero-visual.svg",
                    type="svg",
                    alt="Hero Showcase Visual",
                    status="placeholder",
                )
            )

        return AssetManifest(assets=manifest_items)

    def _guess_extension(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path.lower()
        for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"]:
            if path.endswith(ext):
                return ext
        return ".jpg"

    def _create_svg_placeholder(self, dest_path: str, text: str, width: int = 800, height: int = 500):
        clean_text = re.sub(r"[^\w\s-]", "", text)[:30] or "Visual Asset"
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:0.8" />
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#60a5fa;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#000000;stop-opacity:0" />
    </radialGradient>
  </defs>
  <rect width="100%" height="100%" fill="#0f172a" rx="16" />
  <circle cx="{width//2}" cy="{height//2}" r="{height//3}" fill="url(#glow)" />
  <rect x="40" y="40" width="{width - 80}" height="{height - 80}" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="2" rx="12" stroke-dasharray="8 8" />
  <g transform="translate({width//2}, {height//2 - 20})" text-anchor="middle">
    <path d="M-30,-20 L30,-20 L20,20 L-20,20 Z" fill="url(#grad)" opacity="0.9" />
    <text y="50" font-family="Inter, system-ui, sans-serif" font-size="22" font-weight="600" fill="#f8fafc">{clean_text}</text>
    <text y="78" font-family="Inter, system-ui, sans-serif" font-size="14" fill="#94a3b8">Replicate.AI Visual Vector</text>
  </g>
</svg>"""
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
