"""Automatic Repair Agent: Diagnoses and repairs build/TypeScript/syntax errors up to 3 iterations."""
import os
import re
from typing import Dict, Any, List, Optional
from backend.app.schemas.website_spec import WebsiteSpec
from backend.app.services.llm_provider import LLMProvider


class RepairAgent:
    def __init__(self, llm: LLMProvider, max_iterations: int = 3):
        self.llm = llm
        self.max_iterations = max_iterations

    async def attempt_repair(
        self,
        project_dir: str,
        error_log: str,
        spec: WebsiteSpec,
        iteration: int
    ) -> bool:
        """
        Analyze build error log and apply code repairs to offending files.
        Returns True if a fix was applied.
        """
        if iteration > self.max_iterations:
            return False

        # Identify offending file from error log
        target_file = self._find_failing_file(project_dir, error_log)
        if not target_file or not os.path.exists(target_file):
            target_file = os.path.join(project_dir, "src", "App.tsx")

        rel_path = os.path.relpath(target_file, project_dir)
        with open(target_file, "r", encoding="utf-8") as f:
            original_code = f.read()

        # Generate repaired code
        fixed_code = await self.llm.repair(original_code, error_log, rel_path)

        # Apply common mechanical repairs if LLM didn't change anything
        if fixed_code == original_code or not fixed_code.strip():
            fixed_code = self._apply_rule_based_repairs(original_code, error_log)

        with open(target_file, "w", encoding="utf-8") as f:
            f.write(fixed_code)

        return True

    def _find_failing_file(self, project_dir: str, error_log: str) -> Optional[str]:
        # Search for paths like src/components/Hero.tsx:12:4 or src/App.tsx
        matches = re.findall(r"(src/[a-zA-Z0-9_\-/]+\.(?:tsx|ts|jsx|js|css))", error_log)
        if matches:
            candidate = os.path.join(project_dir, matches[0].replace("/", os.sep))
            if os.path.exists(candidate):
                return candidate
        return None

    def _apply_rule_based_repairs(self, code: str, error_log: str) -> str:
        fixed = code

        # Missing React import
        if "Cannot find name 'React'" in error_log and "import React" not in fixed:
            fixed = "import React from 'react';\n" + fixed

        # Missing Lucide icon imports
        for icon in ["ArrowRight", "CheckCircle2", "Play", "Menu", "X", "Shield", "Zap", "Layers", "Activity"]:
            if f"Cannot find name '{icon}'" in error_log:
                if "from 'lucide-react'" in fixed:
                    fixed = fixed.replace("from 'lucide-react';", f", {icon} }} from 'lucide-react';")
                else:
                    fixed = f"import {{ {icon} }} from 'lucide-react';\n" + fixed

        # TypeScript strict unused variable or any type warning
        if "is declared but its value is never read" in error_log:
            var_match = re.search(r"'([a-zA-Z0-9_]+)' is declared but its value is never read", error_log)
            if var_match:
                unused_var = var_match.group(1)
                fixed = fixed.replace(f"const {unused_var} =", f"// const {unused_var} =")

        return fixed
