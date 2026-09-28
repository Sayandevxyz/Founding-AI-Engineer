"""End-to-End Pipeline Verification Script."""
import asyncio
import os
import sys

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath("."))

from backend.app.models.database import SessionLocal, ProjectModel, init_db
from backend.app.agents.orchestrator import AgentOrchestrator
from backend.app.services.preview_manager import PreviewManager


async def main():
    print("==================================================")
    print("  REPLICATE.AI END-TO-END PIPELINE VERIFICATION   ")
    print("==================================================")
    init_db()
    db = SessionLocal()
    preview_mgr = PreviewManager()
    orch = AgentOrchestrator(db, preview_mgr=preview_mgr)

    project_id = "test-e2e"
    test_url = "https://example.com"

    # Clean existing test record if any
    existing = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if existing:
        db.delete(existing)
        db.commit()

    print(f"\n[1/4] Creating test project for URL: {test_url}")
    model = ProjectModel(
        id=project_id,
        name="Example Domain Benchmark",
        original_url=test_url,
        status="INITIALIZED",
        current_version=1
    )
    db.add(model)
    db.commit()

    async def log_callback(evt):
        print(f"  [AGENT EVENT] {evt.get('progress')}% - {evt.get('step')}", flush=True)

    print("\n[2/4] Executing autonomous reconstruction pipeline...")
    res = await orch.execute_clone_pipeline(project_id, event_callback=log_callback)

    print(f"\nReconstruction completed!")
    print(f"  Status: {res.status}")
    print(f"  Build Passed: {res.validation_result.buildPassed}")
    print(f"  Preview Port: {res.preview_port}")
    print(f"  Approximate Similarity: {res.validation_result.visualSimilarityScore}%")

    assert res.validation_result.buildPassed, "Expected generated project build to pass."
    assert res.preview_port is not None, "Expected preview port to be assigned."

    print("\n[3/4] Testing Natural Language AI Modification Agent...")
    mod_prompt = "Change primary color to blue and make the navbar sticky"
    mod_res = await orch.execute_modification(project_id, mod_prompt, event_callback=log_callback)

    print(f"\nModification completed!")
    print(f"  Current Version: {mod_res.current_version}")
    print(f"  Build Passed: {mod_res.validation_result.buildPassed}")
    print(f"  Versions count: {len(mod_res.versions)}")

    assert mod_res.current_version == 2, "Expected version to increment to 2."
    assert mod_res.validation_result.buildPassed, "Expected modified build to pass."

    print("\n[4/4] Testing Version Rollback to v1...")
    roll_res = await orch.rollback_to_version(project_id, target_version=1)
    print(f"  Rolled back to version: {roll_res.current_version}")
    assert roll_res.current_version == 1, "Expected current version to be 1 after rollback."

    print("\n==================================================")
    print("  ALL PIPELINE STAGES VERIFIED SUCCESSFULLY! [OK]   ")
    print("==================================================")

    # Stop preview server cleanly
    await preview_mgr.stop_preview(project_id)


if __name__ == "__main__":
    asyncio.run(main())
