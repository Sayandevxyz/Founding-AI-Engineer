"""Schemas for Project, Validation, Modifications, and API exchanges."""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from backend.app.schemas.website_spec import WebsiteSpec, AssetManifestItem


class AgentState(str, Enum):
    INITIALIZED = "INITIALIZED"
    DISCOVERING = "DISCOVERING"
    ANALYZING = "ANALYZING"
    EXTRACTING_ASSETS = "EXTRACTING_ASSETS"
    PLANNING = "PLANNING"
    GENERATING = "GENERATING"
    BUILDING = "BUILDING"
    VALIDATING = "VALIDATING"
    REPAIRING = "REPAIRING"
    READY = "READY"
    MODIFYING = "MODIFYING"
    FAILED = "FAILED"


class ValidationResult(BaseModel):
    buildPassed: bool = False
    runtimePassed: bool = False
    consoleErrors: List[str] = Field(default_factory=list)
    brokenImages: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    screenshotPath: Optional[str] = None
    mobileScreenshotPath: Optional[str] = None
    visualSimilarityScore: Optional[float] = None
    similarityExplanation: Optional[str] = None
    checkedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class FileChangePlan(BaseModel):
    file: str
    reason: str
    change: str


class ModificationPlan(BaseModel):
    request: str
    changes: List[FileChangePlan] = Field(default_factory=list)


class ModificationRequest(BaseModel):
    prompt: str


class ProjectVersion(BaseModel):
    version: int
    prompt: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    changedFiles: List[str] = Field(default_factory=list)
    buildPassed: bool = True
    snapshotDir: Optional[str] = None


class ProjectCreateRequest(BaseModel):
    url: str
    name: Optional[str] = None


class ProjectStats(BaseModel):
    aiCalls: int = 0
    estimatedTokens: int = 0
    generationTimeSecs: float = 0.0
    buildAttempts: int = 0
    repairAttempts: int = 0


class ProjectResponse(BaseModel):
    id: str
    name: str
    original_url: str
    status: AgentState
    created_at: str
    updated_at: str
    preview_port: Optional[int] = None
    preview_url: Optional[str] = None
    current_version: int = 1
    stats: ProjectStats = Field(default_factory=ProjectStats)
    website_spec: Optional[WebsiteSpec] = None
    validation_result: Optional[ValidationResult] = None
    versions: List[ProjectVersion] = Field(default_factory=list)
    desktop_screenshot: Optional[str] = None
    mobile_screenshot: Optional[str] = None
    original_desktop_screenshot: Optional[str] = None
    original_mobile_screenshot: Optional[str] = None
    error_message: Optional[str] = None
