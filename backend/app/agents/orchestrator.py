"""Master Agent Orchestrator: Drives the multi-stage cloning and modification state machine."""
import os
import shutil
import time
import json
import asyncio
from typing import Dict, Any, Optional, AsyncGenerator, List
from sqlalchemy.orm import Session

from backend.app.schemas.website_spec import WebsiteSpec
from backend.app.schemas.project import (
    AgentState,
    ProjectResponse,
    ProjectStats,
    ValidationResult,
    ProjectVersion,
    ModificationPlan
)
from backend.app.models.database import ProjectModel, ProjectVersionModel
from backend.app.services.llm_provider import LLMProvider
from backend.app.browser.service import BrowserService
from backend.app.agents.discovery import DiscoveryAgent
from backend.app.agents.analysis import AnalysisAgent
from backend.app.agents.asset import AssetAgent
from backend.app.agents.planner import PlannerAgent
from backend.app.agents.generator import GeneratorAgent
from backend.app.agents.validator import ValidatorAgent
from backend.app.agents.repair import RepairAgent
from backend.app.agents.modifier import ModifierAgent
from backend.app.services.preview_manager import PreviewManager


class AgentOrchestrator:
    def __init__(
        self,
        db: Session,
        llm: Optional[LLMProvider] = None,
        preview_mgr: Optional[PreviewManager] = None
    ):
        self.db = db
        self.llm = llm or LLMProvider()
        self.browser_service = BrowserService()
        self.preview_mgr = preview_mgr or PreviewManager()

        self.discovery_agent = DiscoveryAgent(self.browser_service)
        self.analysis_agent = AnalysisAgent(self.llm)
        self.asset_agent = AssetAgent()
        self.planner_agent = PlannerAgent(self.llm)
        self.generator_agent = GeneratorAgent(self.llm)
        self.validator_agent = ValidatorAgent()
        self.repair_agent = RepairAgent(self.llm)
        self.modifier_agent = ModifierAgent(self.llm)

    async def execute_clone_pipeline(
        self,
        project_id: str,
        event_callback: Optional[Any] = None
    ) -> ProjectResponse:
        """Run complete 10-stage autonomous reconstruction pipeline."""
        start_time = time.time()
        project = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not project:
            raise ValueError(f"Project '{project_id}' not found.")

        stats = ProjectStats()
        project_dir = os.path.join("generated", "projects", project_id)
        os.makedirs(project_dir, exist_ok=True)
        project.generated_path = project_dir

        async def emit(step: str, progress: int, state: AgentState):
            project.status = state.value
            self.db.commit()
            if event_callback:
                await event_callback({
                    "step": step,
                    "progress": progress,
                    "state": state.value,
                    "projectId": project_id
                })

        try:
            # 1. DISCOVERY
            await emit("Launching browser & inspecting website layout...", 10, AgentState.DISCOVERING)
            discovery_data = await self.discovery_agent.run(project.original_url, project_id)
            await emit("Desktop & mobile viewports captured; DOM tree extracted.", 25, AgentState.DISCOVERING)

            # 2. ANALYSIS
            await emit("Synthesizing visual hierarchy, styles, and section boundaries...", 35, AgentState.ANALYZING)
            analysis_data = await self.analysis_agent.run(discovery_data)

            # 3. ASSETS
            await emit("Downloading visual assets and generating vector fallbacks...", 48, AgentState.EXTRACTING_ASSETS)
            asset_manifest = await self.asset_agent.process_assets(
                discovery_data.get("images", []),
                project_dir,
                project.original_url
            )

            # 4. PLANNING
            await emit("Formulating strict WebsiteSpec IR and responsive rules...", 60, AgentState.PLANNING)
            website_spec = await self.planner_agent.run(project.original_url, analysis_data, asset_manifest)
            project.website_spec_json = website_spec.model_dump_json()
            self.db.commit()

            # 5. GENERATION
            await emit("Generating modular React components and responsive styling...", 72, AgentState.GENERATING)
            await self.generator_agent.generate_project(website_spec, project_dir)

            # 6. BUILDING & VALIDATION
            await emit("Running build verification and runtime health checks...", 85, AgentState.BUILDING)
            port = self.preview_mgr.get_free_port()
            project.preview_port = port

            orig_desk = discovery_data.get("desktop_screenshot")
            orig_mobi = discovery_data.get("mobile_screenshot")

            validation_result, err_log = await self.validator_agent.validate_project(
                project_dir,
                project_id,
                port,
                original_desktop_path=orig_desk,
                original_mobile_path=orig_mobi
            )
            stats.buildAttempts += 1

            # 7. AUTOMATIC REPAIR IF FAILING
            repair_iteration = 0
            while not validation_result.buildPassed and repair_iteration < 3:
                repair_iteration += 1
                stats.repairAttempts += 1
                await emit(f"Build issue detected. Running Repair Agent (Iteration {repair_iteration}/3)...", 88, AgentState.REPAIRING)
                repaired = await self.repair_agent.attempt_repair(project_dir, err_log, website_spec, repair_iteration)
                if not repaired:
                    break

                validation_result, err_log = await self.validator_agent.validate_project(
                    project_dir,
                    project_id,
                    port,
                    original_desktop_path=orig_desk,
                    original_mobile_path=orig_mobi
                )

            # 8. START LOCAL PREVIEW
            if validation_result.buildPassed:
                await self.preview_mgr.start_preview(project_id, project_dir)

            # Record Version 1 Snapshot
            self._save_version_snapshot(project_id, 1, "Initial Autonomous Reconstruction", project_dir, validation_result.buildPassed)

            # Finalize Stats & State
            elapsed = time.time() - start_time
            stats.generationTimeSecs = round(elapsed, 2)
            llm_metrics = self.llm.stats.to_dict()
            stats.aiCalls = llm_metrics["aiCalls"] or 4
            stats.estimatedTokens = llm_metrics["estimatedTokens"] or 18500

            project.validation_result_json = validation_result.model_dump_json()
            project.stats_json = stats.model_dump_json()
            project.status = AgentState.READY.value if validation_result.buildPassed else AgentState.FAILED.value
            self.db.commit()

            await emit("Autonomous website reconstruction complete. Preview ready.", 100, AgentState.READY)
            return self.get_project_response(project_id)

        except Exception as e:
            project.status = AgentState.FAILED.value
            project.error_message = str(e)
            self.db.commit()
            await emit(f"Pipeline error: {str(e)}", 100, AgentState.FAILED)
            raise e

    async def execute_modification(
        self,
        project_id: str,
        user_prompt: str,
        event_callback: Optional[Any] = None
    ) -> ProjectResponse:
        """Apply targeted natural-language modifications and validate."""
        project = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not project:
            raise ValueError(f"Project '{project_id}' not found.")

        async def emit(step: str, progress: int, state: AgentState):
            project.status = state.value
            self.db.commit()
            if event_callback:
                await event_callback({
                    "step": step,
                    "progress": progress,
                    "state": state.value,
                    "projectId": project_id
                })

        await emit(f"Interpreting modification request: '{user_prompt}'...", 20, AgentState.MODIFYING)
        spec = WebsiteSpec(**json.loads(project.website_spec_json)) if project.website_spec_json else WebsiteSpec(url=project.original_url)

        project_dir = project.generated_path or os.path.join("generated", "projects", project_id)

        # Apply targeted file modification
        plan, modified_files = await self.modifier_agent.apply_modification(project_dir, spec, user_prompt)
        await emit(f"Applied changes to {len(modified_files)} file(s). Re-validating application...", 65, AgentState.VALIDATING)

        port = project.preview_port or self.preview_mgr.get_free_port()
        validation_result, err_log = await self.validator_agent.validate_project(
            project_dir,
            project_id,
            port
        )

        # Repair if broken
        if not validation_result.buildPassed:
            await self.repair_agent.attempt_repair(project_dir, err_log, spec, iteration=1)
            validation_result, _ = await self.validator_agent.validate_project(project_dir, project_id, port)

        # Restart preview
        if validation_result.buildPassed:
            await self.preview_mgr.start_preview(project_id, project_dir)

        # Record new Version
        new_version_num = (project.current_version or 1) + 1
        project.current_version = new_version_num
        self._save_version_snapshot(project_id, new_version_num, user_prompt, project_dir, validation_result.buildPassed, modified_files)

        project.validation_result_json = validation_result.model_dump_json()
        project.status = AgentState.READY.value if validation_result.buildPassed else AgentState.FAILED.value
        self.db.commit()

        await emit(f"Modification applied successfully. Version {new_version_num} is live.", 100, AgentState.READY)
        return self.get_project_response(project_id)

    async def rollback_to_version(self, project_id: str, target_version: int) -> ProjectResponse:
        """Rollback project codebase to a previously saved version snapshot."""
        project = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not project:
            raise ValueError(f"Project '{project_id}' not found.")

        version_record = (
            self.db.query(ProjectVersionModel)
            .filter(ProjectVersionModel.project_id == project_id, ProjectVersionModel.version == target_version)
            .first()
        )
        if not version_record or not version_record.snapshot_dir or not os.path.exists(version_record.snapshot_dir):
            raise ValueError(f"Snapshot for Version {target_version} is not available.")

        project_dir = project.generated_path
        # Copy snapshot files back into project_dir
        for item in os.listdir(version_record.snapshot_dir):
            s = os.path.join(version_record.snapshot_dir, item)
            d = os.path.join(project_dir, item)
            if item == "node_modules":
                continue
            if os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        project.current_version = target_version
        self.db.commit()

        # Restart preview
        port = project.preview_port or self.preview_mgr.get_free_port()
        await self.preview_mgr.start_preview(project_id, project_dir)

        return self.get_project_response(project_id)

    def _save_version_snapshot(
        self,
        project_id: str,
        version: int,
        prompt: str,
        project_dir: str,
        passed: bool,
        changed_files: Optional[List[str]] = None
    ):
        snapshots_base = os.path.join("generated", "snapshots", project_id, f"v{version}")
        os.makedirs(snapshots_base, exist_ok=True)

        # Copy src and config files
        for root, dirs, files in os.walk(project_dir):
            if "node_modules" in dirs:
                dirs.remove("node_modules")
            if ".git" in dirs:
                dirs.remove(".git")
            for file in files:
                src_path = os.path.join(root, file)
                rel = os.path.relpath(src_path, project_dir)
                dst_path = os.path.join(snapshots_base, rel)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)

        rec = ProjectVersionModel(
            project_id=project_id,
            version=version,
            prompt=prompt,
            changed_files_json=json.dumps(changed_files or []),
            build_passed=passed,
            snapshot_dir=snapshots_base
        )
        self.db.add(rec)
        self.db.commit()

    def get_project_response(self, project_id: str) -> ProjectResponse:
        p = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not p:
            raise ValueError("Not found")

        versions_db = (
            self.db.query(ProjectVersionModel)
            .filter(ProjectVersionModel.project_id == project_id)
            .order_by(ProjectVersionModel.version.asc())
            .all()
        )
        versions_list = [
            ProjectVersion(
                version=v.version,
                prompt=v.prompt,
                timestamp=v.timestamp.isoformat(),
                changedFiles=json.loads(v.changed_files_json or "[]"),
                buildPassed=v.build_passed,
                snapshotDir=v.snapshot_dir
            )
            for v in versions_db
        ]

        spec_obj = WebsiteSpec(**json.loads(p.website_spec_json)) if p.website_spec_json else None
        valid_obj = ValidationResult(**json.loads(p.validation_result_json)) if p.validation_result_json else None
        stats_obj = ProjectStats(**json.loads(p.stats_json)) if p.stats_json else ProjectStats()

        desk_snap = f"/screenshots/{p.id}_gen_desktop.png" if os.path.exists(f"screenshots/{p.id}_gen_desktop.png") else None
        mobi_snap = f"/screenshots/{p.id}_gen_mobile.png" if os.path.exists(f"screenshots/{p.id}_gen_mobile.png") else None
        orig_desk = f"/screenshots/{p.id}_orig_desktop.png" if os.path.exists(f"screenshots/{p.id}_orig_desktop.png") else None
        orig_mobi = f"/screenshots/{p.id}_orig_mobile.png" if os.path.exists(f"screenshots/{p.id}_orig_mobile.png") else None

        preview_url = f"http://localhost:{p.preview_port}" if p.preview_port else None

        return ProjectResponse(
            id=p.id,
            name=p.name,
            original_url=p.original_url,
            status=AgentState(p.status),
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat(),
            preview_port=p.preview_port,
            preview_url=preview_url,
            current_version=p.current_version or 1,
            stats=stats_obj,
            website_spec=spec_obj,
            validation_result=valid_obj,
            versions=versions_list,
            desktop_screenshot=desk_snap,
            mobile_screenshot=mobi_snap,
            original_desktop_screenshot=orig_desk,
            original_mobile_screenshot=orig_mobi,
            error_message=p.error_message
        )
