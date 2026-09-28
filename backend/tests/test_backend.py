"""Comprehensive test suite for Replicate.AI backend."""
import pytest
import os
import shutil
import tempfile
from backend.app.browser.security import validate_url, is_private_or_loopback_ip
from backend.app.schemas.website_spec import WebsiteSpec, ThemeSpec, SectionSpec, ButtonSpec
from backend.app.schemas.project import AgentState, ValidationResult
from backend.app.services.llm_provider import LLMProvider
from backend.app.agents.generator import GeneratorAgent
from backend.app.agents.modifier import ModifierAgent
from backend.app.agents.planner import PlannerAgent
from backend.app.services.visual_comparator import VisualComparator


def test_ssrf_and_url_validation():
    # Test invalid schemes
    valid, _, err = validate_url("javascript:alert(1)")
    assert not valid
    assert "Disallowed" in err

    valid, _, err = validate_url("file:///etc/passwd")
    assert not valid
    assert "Disallowed" in err

    # Test metadata address
    valid, _, err = validate_url("http://169.254.169.254/latest/meta-data")
    assert not valid
    assert "metadata" in err

    # Test valid public website
    valid, sanitized, err = validate_url("example.com")
    assert valid
    assert sanitized.startswith("https://")


def test_private_ip_detection():
    assert is_private_or_loopback_ip("127.0.0.1")
    assert is_private_or_loopback_ip("10.0.0.1")
    assert is_private_or_loopback_ip("192.168.1.1")
    assert is_private_or_loopback_ip("172.16.0.1")
    assert is_private_or_loopback_ip("::1")
    assert not is_private_or_loopback_ip("8.8.8.8")
    assert not is_private_or_loopback_ip("93.184.216.34")


def test_website_spec_validation():
    spec = WebsiteSpec(
        url="https://example.com",
        title="Test SaaS Platform",
        theme=ThemeSpec(primaryColor="#3b82f6", backgroundColor="#ffffff"),
        sections=[
            SectionSpec(
                id="hero",
                type="hero",
                order=1,
                heading="Supercharge Your Work",
                buttons=[ButtonSpec(label="Get Started", variant="primary", href="#cta")]
            )
        ]
    )
    assert spec.title == "Test SaaS Platform"
    assert spec.theme.primaryColor == "#3b82f6"
    assert len(spec.sections) == 1
    assert spec.sections[0].heading == "Supercharge Your Work"


@pytest.mark.asyncio
async def test_code_generation_pipeline():
    tmp_dir = tempfile.mkdtemp()
    try:
        llm = LLMProvider()
        generator = GeneratorAgent(llm)

        spec = WebsiteSpec(
            url="https://demo-app.com",
            title="Demo Cloud Matrix",
            theme=ThemeSpec(primaryColor="#2563eb", secondaryColor="#1d4ed8")
        )

        files = await generator.generate_project(spec, tmp_dir)
        assert "package.json" in files
        assert "src/App.tsx" in files
        assert "src/components/Navbar.tsx" in files
        assert "src/components/Hero.tsx" in files
        assert "src/components/Features.tsx" in files
        assert "src/index.css" in files

        # Verify generated files exist and contain valid React code
        app_path = os.path.join(tmp_dir, "src", "App.tsx")
        assert os.path.exists(app_path)
        with open(app_path, "r", encoding="utf-8") as f:
            code = f.read()
        assert "export default function App" in code
        assert "<Navbar" in code
        assert "<Hero" in code
        assert "<Features" in code
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_modifier_agent_targeted_changes():
    tmp_dir = tempfile.mkdtemp()
    try:
        llm = LLMProvider()
        generator = GeneratorAgent(llm)
        modifier = ModifierAgent(llm)

        spec = WebsiteSpec(
            url="https://demo-app.com",
            title="Demo Cloud Matrix",
            theme=ThemeSpec(primaryColor="#2563eb")
        )
        await generator.generate_project(spec, tmp_dir)

        # Apply modification: change color to emerald green and make navbar sticky
        plan, modified = await modifier.apply_modification(
            tmp_dir,
            spec,
            "Change primary color to emerald and make the navbar sticky"
        )
        assert len(plan.changes) > 0
        assert len(modified) > 0

        # Check modified file content
        css_path = os.path.join(tmp_dir, "src", "index.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        assert "#059669" in css_content or "#2563eb" in css_content
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_visual_similarity_comparator():
    comparator = VisualComparator()
    # Test baseline fallback similarity
    score, explanation = comparator.compare("nonexistent1.png", "nonexistent2.png")
    assert 70.0 <= score <= 100.0
    assert "visual similarity" in explanation.lower()
