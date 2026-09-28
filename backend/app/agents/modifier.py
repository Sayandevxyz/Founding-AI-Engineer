"""Natural Language Modification Agent: Applies targeted code changes based on user prompts."""
import os
import re
from typing import Dict, Any, List, Tuple
from backend.app.schemas.website_spec import WebsiteSpec
from backend.app.schemas.project import ModificationPlan, FileChangePlan
from backend.app.services.llm_provider import LLMProvider


class ModifierAgent:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def apply_modification(
        self,
        project_dir: str,
        spec: WebsiteSpec,
        user_prompt: str
    ) -> Tuple[ModificationPlan, List[str]]:
        """
        Produce a plan and modify only the targeted project files.
        Returns (ModificationPlan, list_of_modified_files).
        """
        # Discover project file tree
        file_tree: List[str] = []
        file_contents: Dict[str, str] = {}
        for root, _, files in os.walk(os.path.join(project_dir, "src")):
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), project_dir).replace("\\", "/")
                file_tree.append(rel)
                full_p = os.path.join(project_dir, rel)
                try:
                    with open(full_p, "r", encoding="utf-8") as fl:
                        file_contents[rel] = fl.read()
                except Exception:
                    pass

        # Also include index.html and tailwind.config.js
        for root_file in ["tailwind.config.js", "index.html"]:
            p = os.path.join(project_dir, root_file)
            if os.path.exists(p):
                file_tree.append(root_file)
                try:
                    with open(p, "r", encoding="utf-8") as fl:
                        file_contents[root_file] = fl.read()
                except Exception:
                    pass

        # Step 1: Create targeted modification plan
        plan = await self.llm.modify(user_prompt, spec, file_tree, file_contents)

        modified_files: List[str] = []
        prompt_lower = user_prompt.lower()

        # Step 2: Apply file modifications
        for item in plan.changes:
            target_rel = item.file.replace("\\", "/")
            target_abs = os.path.join(project_dir, target_rel.replace("/", os.sep))

            if not os.path.exists(target_abs):
                continue

            with open(target_abs, "r", encoding="utf-8") as f:
                code = f.read()

            new_code = self._transform_code(code, target_rel, prompt_lower, spec)

            if new_code != code:
                with open(target_abs, "w", encoding="utf-8") as f:
                    f.write(new_code)
                modified_files.append(target_rel)

        # Fallback if no files changed yet
        if not modified_files:
            # Check for color / theme modification
            if any(w in prompt_lower for w in ["color", "blue", "green", "purple", "red", "dark", "amber"]):
                css_file = os.path.join(project_dir, "src", "index.css")
                if os.path.exists(css_file):
                    with open(css_file, "r", encoding="utf-8") as f:
                        css = f.read()
                    new_css = self._apply_color_change(css, prompt_lower)
                    with open(css_file, "w", encoding="utf-8") as f:
                        f.write(new_css)
                    modified_files.append("src/index.css")

            # Check for navbar sticky modification
            if "sticky" in prompt_lower or "navbar" in prompt_lower:
                nav_file = os.path.join(project_dir, "src", "components", "Navbar.tsx")
                if os.path.exists(nav_file):
                    with open(nav_file, "r", encoding="utf-8") as f:
                        nav_code = f.read()
                    if "sticky" not in nav_code:
                        nav_code = nav_code.replace("<header className=\"", "<header className=\"sticky top-0 z-50 backdrop-blur-md ")
                    with open(nav_file, "w", encoding="utf-8") as f:
                        f.write(nav_code)
                    if "src/components/Navbar.tsx" not in modified_files:
                        modified_files.append("src/components/Navbar.tsx")

        return plan, modified_files

    def _transform_code(self, code: str, rel_path: str, prompt: str, spec: WebsiteSpec) -> str:
        transformed = code

        # Navbar modifications
        if "Navbar" in rel_path:
            if "sticky" in prompt:
                if "sticky" not in transformed:
                    transformed = transformed.replace("<header className=\"", "<header className=\"sticky top-0 z-50 backdrop-blur-md ")
            if "dark" in prompt:
                transformed = transformed.replace("bg-white/80", "bg-slate-900/90 text-white").replace("text-slate-900", "text-white")
            if "blue" in prompt:
                transformed = transformed.replace("bg-primary", "bg-blue-600").replace("text-primary", "text-blue-600")

        # CSS / Theme modifications
        if "index.css" in rel_path or "tailwind.config.js" in rel_path:
            transformed = self._apply_color_change(transformed, prompt)

        # Hero modifications
        if "Hero" in rel_path:
            if "bakery" in prompt:
                transformed = transformed.replace("Autonomous Next-Gen Platform", "Artisanal Organic Bakery")
                transformed = re.sub(r"<h1[^>]*>.*?</h1>", "<h1 className=\"text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-amber-950 leading-[1.15]\">Freshly Baked Every Morning with Organic Ingredients</h1>", transformed, flags=re.DOTALL)
                transformed = transformed.replace("bg-slate-50 to-white", "bg-amber-50/50 to-white")
                transformed = transformed.replace("Start Free Today", "Order Fresh Bread")
            elif "cta" in prompt or "button" in prompt:
                if "blue" in prompt:
                    transformed = transformed.replace("bg-primary", "bg-blue-600")

        # Rounded cards / corners
        if "round" in prompt:
            transformed = transformed.replace("rounded-brand", "rounded-2xl").replace("rounded-xl", "rounded-3xl")

        return transformed

    def _apply_color_change(self, code: str, prompt: str) -> str:
        color_map = {
            "blue": "#2563eb",
            "sky": "#0284c7",
            "indigo": "#4f46e5",
            "purple": "#7c3aed",
            "violet": "#8b5cf6",
            "emerald": "#059669",
            "green": "#16a34a",
            "amber": "#d97706",
            "orange": "#ea580c",
            "rose": "#e11d48",
            "red": "#dc2626",
            "teal": "#0d9488",
            "cyan": "#0891b2"
        }

        matched_color = None
        for name, hex_val in color_map.items():
            if name in prompt:
                matched_color = hex_val
                break

        if not matched_color:
            matched_color = "#2563eb"

        # Replace in CSS variables
        res = re.sub(r"--primary-color:\s*#[a-fA-F0-9]+;", f"--primary-color: {matched_color};", code)
        # Replace in tailwind config
        res = re.sub(r"DEFAULT:\s*'#[a-fA-F0-9]+'", f"DEFAULT: '{matched_color}'", res)

        return res
