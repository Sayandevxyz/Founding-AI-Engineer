"""API Endpoints for Project lifecycle, analysis, generation, modification, and streaming."""
import json
import uuid
import asyncio
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.models.database import get_db, ProjectModel, ProjectVersionModel
from backend.app.schemas.project import (
    ProjectCreateRequest,
    ProjectResponse,
    ModificationRequest,
    ValidationResult,
    ProjectVersion
)
from backend.app.browser.security import validate_url
from backend.app.agents.orchestrator import AgentOrchestrator
from backend.app.services.preview_manager import PreviewManager

router = APIRouter(prefix="/api/projects", tags=["projects"])
preview_manager = PreviewManager()

# Global in-memory broadcast queues for SSE by project_id
event_queues: Dict[str, List[asyncio.Queue]] = {}


def get_orchestrator(db: Session = Depends(get_db)) -> AgentOrchestrator:
    return AgentOrchestrator(db=db, preview_mgr=preview_manager)


async def broadcast_event(project_id: str, data: Dict[str, Any]):
    if project_id in event_queues:
        for q in event_queues[project_id]:
            await q.put(data)


@router.post("", response_model=ProjectResponse)
async def create_project(
    req: ProjectCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new project and validate URL security."""
    is_valid, sanitized_url, err = validate_url(req.url, allow_localhost=True)
    if not is_valid:
        raise HTTPException(status_code=400, detail=err)

    project_id = str(uuid.uuid4())[:8]
    derived_name = req.name or sanitized_url.replace("https://", "").replace("http://", "").split("/")[0]

    model = ProjectModel(
        id=project_id,
        name=derived_name,
        original_url=sanitized_url,
        status="INITIALIZED",
        current_version=1
    )
    db.add(model)
    db.commit()

    orch = AgentOrchestrator(db, preview_mgr=preview_manager)
    return orch.get_project_response(project_id)


@router.get("", response_model=List[ProjectResponse])
async def list_projects(db: Session = Depends(get_db)):
    """List recent reconstruction projects."""
    projects = db.query(ProjectModel).order_by(ProjectModel.created_at.desc()).all()
    orch = AgentOrchestrator(db, preview_mgr=preview_manager)
    return [orch.get_project_response(p.id) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: Session = Depends(get_db)):
    """Fetch project details, WebsiteSpec, versions, and validation state."""
    orch = AgentOrchestrator(db, preview_mgr=preview_manager)
    try:
        return orch.get_project_response(project_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Project not found.")


@router.post("/{project_id}/generate", response_model=ProjectResponse)
async def generate_project_endpoint(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Execute complete autonomous reconstruction pipeline."""
    orch = AgentOrchestrator(db, preview_mgr=preview_manager)

    async def callback(evt):
        await broadcast_event(project_id, evt)

    try:
        return await orch.execute_clone_pipeline(project_id, event_callback=callback)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/modify", response_model=ProjectResponse)
async def modify_project_endpoint(
    project_id: str,
    req: ModificationRequest,
    db: Session = Depends(get_db)
):
    """Modify generated frontend using natural language prompt."""
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    orch = AgentOrchestrator(db, preview_mgr=preview_manager)

    async def callback(evt):
        await broadcast_event(project_id, evt)

    try:
        return await orch.execute_modification(project_id, req.prompt.strip(), event_callback=callback)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/rollback", response_model=ProjectResponse)
async def rollback_endpoint(
    project_id: str,
    version: int = Query(..., description="Target version number to restore"),
    db: Session = Depends(get_db)
):
    """Roll back to an earlier version snapshot."""
    orch = AgentOrchestrator(db, preview_mgr=preview_manager)
    try:
        return await orch.rollback_to_version(project_id, version)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/events")
async def sse_events(project_id: str):
    """Server-Sent Events endpoint streaming pipeline progress and agent logs."""
    q: asyncio.Queue = asyncio.Queue()
    if project_id not in event_queues:
        event_queues[project_id] = []
    event_queues[project_id].append(q)

    async def event_generator():
        try:
            while True:
                data = await q.get()
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("progress") == 100 or data.get("state") in ["READY", "FAILED"]:
                    break
        except asyncio.CancelledError:
            pass
        finally:
            if project_id in event_queues and q in event_queues[project_id]:
                event_queues[project_id].remove(q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/{project_id}/preview")
async def get_preview_info(project_id: str, db: Session = Depends(get_db)):
    """Retrieve preview server URL and active port."""
    p = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found.")

    port = p.preview_port
    url = f"http://localhost:{port}" if port else None
    return {
        "projectId": project_id,
        "previewPort": port,
        "previewUrl": url,
        "status": p.status
    }


@router.get("/{project_id}/code")
async def get_project_code(project_id: str, file_path: str = "src/App.tsx", db: Session = Depends(get_db)):
    """Inspect generated file contents for code editor."""
    import os
    p = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not p or not p.generated_path:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Guard against directory traversal
    clean_rel = os.path.normpath(file_path).replace("\\", "/")
    if clean_rel.startswith("..") or clean_rel.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid file path.")

    target_abs = os.path.join(p.generated_path, clean_rel.replace("/", os.sep))
    if not os.path.exists(target_abs):
        raise HTTPException(status_code=404, detail=f"File '{file_path}' not found.")

    with open(target_abs, "r", encoding="utf-8") as f:
        content = f.read()

    # Discover all code files for tree
    tree = []
    for root, _, files in os.walk(p.generated_path):
        if "node_modules" in root or ".git" in root or "dist" in root:
            continue
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), p.generated_path).replace("\\", "/")
            tree.append(rel)

    return {
        "file": clean_rel,
        "content": content,
        "fileTree": sorted(tree)
    }
