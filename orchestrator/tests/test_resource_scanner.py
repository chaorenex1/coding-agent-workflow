#!/usr/bin/env python3
"""
Test suite for ResourceScanner - Auto-discovery functionality.

Tests convention-over-configuration approach for Skills, Commands, Agents, Prompts.
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# Windows encoding fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestrator.core.resource_scanner import (
    ResourceScanner,
    SkillDetector,
    CommandDetector,
    AgentDetector,
    PromptDetector,
    DiscoveredResource
)
from orchestrator.core.config_loader import ResourceType


def create_test_environment():
    """Create a temporary test directory structure."""
    test_dir = Path(tempfile.mkdtemp(prefix="scanner_test_"))

    # Create directory structure
    (test_dir / "skills").mkdir()
    (test_dir / "commands").mkdir()
    (test_dir / "agents").mkdir()
    (test_dir / "prompts").mkdir()

    # === SKILL 1: Directory with SKILL.md ===
    skill1_dir = test_dir / "skills" / "test-skill-1"
    skill1_dir.mkdir()

    (skill1_dir / "SKILL.md").write_text("""---
name: test-skill-1
description: Test skill with marker file
backend: claude
temperature: 0.7
dependencies:
  - command:git-diff
---

# Test Skill 1

This is a test skill discovered via SKILL.md marker file.

## Capabilities

- Feature A
- Feature B
""", encoding='utf-8')

    (skill1_dir / "main.py").write_text("""
def execute(request):
    return {"success": True, "output": "Test skill 1"}
""", encoding='utf-8')

    # === SKILL 2: Standalone YAML ===
    (test_dir / "skills" / "test-skill-2.yaml").write_text("""
name: test-skill-2
description: Standalone YAML skill
backend: gemini
enabled: true
""", encoding='utf-8')

    # === SKILL 3: Directory with skill.yaml ===
    skill3_dir = test_dir / "skills" / "test-skill-3"
    skill3_dir.mkdir()

    (skill3_dir / "skill.yaml").write_text("""
name: test-skill-3
description: Skill with explicit YAML config
backend: codex
priority: 90
""", encoding='utf-8')

    (skill3_dir / "test_skill_3.py").write_text("""
def run():
    pass
""", encoding='utf-8')

    # === COMMAND 1: Directory with COMMAND.md ===
    cmd1_dir = test_dir / "commands" / "git-shortcuts"
    cmd1_dir.mkdir()

    (cmd1_dir / "COMMAND.md").write_text("""---
name: git-shortcuts
description: Git command shortcuts
---

# Git Shortcuts

## Command

```bash
git status -sb
```
""", encoding='utf-8')

    # === COMMAND 2: Standalone YAML ===
    (test_dir / "commands" / "docker-utils.yaml").write_text("""
name: docker-utils
description: Docker utility commands
command: docker ps -a
""", encoding='utf-8')

    # === AGENT 1: Directory with AGENT.md ===
    agent1_dir = test_dir / "agents" / "custom-explorer"
    agent1_dir.mkdir()

    (agent1_dir / "AGENT.md").write_text("""---
name: custom-explorer
description: Custom code explorer
agent_type: explore
---

# Custom Explorer

Advanced code exploration agent.
""", encoding='utf-8')

    # === AGENT 2: Standalone YAML ===
    (test_dir / "agents" / "code-analyzer.yaml").write_text("""
name: code-analyzer
description: Code analysis agent
agent_type: general
""", encoding='utf-8')

    # === PROMPT 1: Directory with PROMPT.md ===
    prompt1_dir = test_dir / "prompts" / "code-review"
    prompt1_dir.mkdir()

    (prompt1_dir / "PROMPT.md").write_text("""---
name: code-review
description: Code review prompt template
---

# Code Review Template

## Template

```
Please review the following code:

{code}

Focus areas: {focus_areas}
```
""", encoding='utf-8')

    # === PROMPT 2: Standalone YAML ===
    (test_dir / "prompts" / "api-doc.yaml").write_text("""
name: api-doc
description: API documentation prompt
template: |
  Generate API documentation for:

  {api_code}
variables:
  - api_code
""", encoding='utf-8')

    return test_dir


def test_skill_detector():
    """Test SkillDetector for auto-discovering skills."""
    print("\n" + "="*80)
    print("TEST 1: SkillDetector")
    print("="*80)

    test_dir = create_test_environment()

    try:
        detector = SkillDetector(source="project")
        skills_dir = test_dir / "skills"

        discovered = detector.scan_directory(skills_dir)

        print(f"\n✓ Discovered {len(discovered)} skills")

        assert len(discovered) == 3, f"Expected 3 skills, got {len(discovered)}"

        # Check each skill
        skill_names = {s.name for s in discovered}
        assert "test-skill-1" in skill_names, "test-skill-1 not found"
        assert "test-skill-2" in skill_names, "test-skill-2 not found"
        assert "test-skill-3" in skill_names, "test-skill-3 not found"

        # Verify discovery methods
        for skill in discovered:
            print(f"\n  Skill: {skill.name}")
            print(f"    Method: {skill.discovery_method}")
            print(f"    Path: {skill.path}")
            print(f"    Description: {skill.description[:50]}...")

            if skill.name == "test-skill-1":
                assert skill.discovery_method == "directory_convention"
                assert skill.marker_file is not None
                assert skill.entry_point is not None
                assert "marker file" in skill.description

            elif skill.name == "test-skill-2":
                assert skill.discovery_method == "yaml_file"
                assert skill.config_data.get('backend') == 'gemini'

            elif skill.name == "test-skill-3":
                assert skill.discovery_method == "yaml_file"
                assert skill.config_data.get('priority') == 90

        print("\n✅ SkillDetector test PASSED")

    finally:
        shutil.rmtree(test_dir)


def test_command_detector():
    """Test CommandDetector for auto-discovering commands."""
    print("\n" + "="*80)
    print("TEST 2: CommandDetector")
    print("="*80)

    test_dir = create_test_environment()

    try:
        detector = CommandDetector(source="project")
        commands_dir = test_dir / "commands"

        discovered = detector.scan_directory(commands_dir)

        print(f"\n✓ Discovered {len(discovered)} commands")

        assert len(discovered) == 2, f"Expected 2 commands, got {len(discovered)}"

        for cmd in discovered:
            print(f"\n  Command: {cmd.name}")
            print(f"    Method: {cmd.discovery_method}")
            print(f"    Command: {cmd.config_data.get('command', 'N/A')}")

            if cmd.name == "git-shortcuts":
                assert cmd.discovery_method == "directory_convention"
                assert "git status" in cmd.config_data.get('command', '')

            elif cmd.name == "docker-utils":
                assert cmd.discovery_method == "yaml_file"
                assert "docker ps" in cmd.config_data.get('command', '')

        print("\n✅ CommandDetector test PASSED")

    finally:
        shutil.rmtree(test_dir)


def test_agent_detector():
    """Test AgentDetector for auto-discovering agents."""
    print("\n" + "="*80)
    print("TEST 3: AgentDetector")
    print("="*80)

    test_dir = create_test_environment()

    try:
        detector = AgentDetector(source="project")
        agents_dir = test_dir / "agents"

        discovered = detector.scan_directory(agents_dir)

        print(f"\n✓ Discovered {len(discovered)} agents")

        assert len(discovered) == 2, f"Expected 2 agents, got {len(discovered)}"

        for agent in discovered:
            print(f"\n  Agent: {agent.name}")
            print(f"    Method: {agent.discovery_method}")
            print(f"    Type: {agent.config_data.get('agent_type')}")

            assert 'agent_type' in agent.config_data, f"{agent.name} missing agent_type"

        print("\n✅ AgentDetector test PASSED")

    finally:
        shutil.rmtree(test_dir)


def test_prompt_detector():
    """Test PromptDetector for auto-discovering prompts."""
    print("\n" + "="*80)
    print("TEST 4: PromptDetector")
    print("="*80)

    test_dir = create_test_environment()

    try:
        detector = PromptDetector(source="project")
        prompts_dir = test_dir / "prompts"

        discovered = detector.scan_directory(prompts_dir)

        print(f"\n✓ Discovered {len(discovered)} prompts")

        assert len(discovered) == 2, f"Expected 2 prompts, got {len(discovered)}"

        for prompt in discovered:
            print(f"\n  Prompt: {prompt.name}")
            print(f"    Method: {prompt.discovery_method}")
            print(f"    Has template: {'template' in prompt.config_data}")
            print(f"    Variables: {prompt.config_data.get('variables', [])}")

            if prompt.name == "code-review":
                assert 'template' in prompt.config_data
                assert 'code' in prompt.config_data.get('variables', [])
                assert 'focus_areas' in prompt.config_data.get('variables', [])

            elif prompt.name == "api-doc":
                assert 'template' in prompt.config_data
                assert 'api_code' in prompt.config_data.get('variables', [])

        print("\n✅ PromptDetector test PASSED")

    finally:
        shutil.rmtree(test_dir)


def test_resource_scanner():
    """Test ResourceScanner scanning all resource types."""
    print("\n" + "="*80)
    print("TEST 5: ResourceScanner (All Types)")
    print("="*80)

    test_dir = create_test_environment()

    try:
        scanner = ResourceScanner()

        results = scanner.scan_all(test_dir, source="project")

        print(f"\n✓ Scan complete")
        print(f"  Skills: {len(results[ResourceType.SKILL])}")
        print(f"  Commands: {len(results[ResourceType.COMMAND])}")
        print(f"  Agents: {len(results[ResourceType.AGENT])}")
        print(f"  Prompts: {len(results[ResourceType.PROMPT])}")

        assert len(results[ResourceType.SKILL]) == 3
        assert len(results[ResourceType.COMMAND]) == 2
        assert len(results[ResourceType.AGENT]) == 2
        assert len(results[ResourceType.PROMPT]) == 2

        total = sum(len(items) for items in results.values())
        print(f"\n  Total resources: {total}")
        assert total == 9

        # Test conversion to config
        for resource_type, resources in results.items():
            for discovered in resources:
                config = scanner.convert_to_config(discovered)
                print(f"\n  Converted {resource_type.value}: {config.name}")
                assert config.name == discovered.name
                assert config.source == discovered.source

        print("\n✅ ResourceScanner test PASSED")

    finally:
        shutil.rmtree(test_dir)


def test_integration_with_config_loader():
    """Test integration with ConfigLoader."""
    print("\n" + "="*80)
    print("TEST 6: ConfigLoader Integration")
    print("="*80)

    test_dir = create_test_environment()

    try:
        from orchestrator.core.config_loader import ConfigLoader
        import logging
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

        # Debug: Check test environment
        print(f"\n  Test directory: {test_dir}")
        print(f"  Skills dir exists: {(test_dir / 'skills').exists()}")
        print(f"  Commands dir exists: {(test_dir / 'commands').exists()}")
        print(f"  Agents dir exists: {(test_dir / 'agents').exists()}")
        print(f"  Prompts dir exists: {(test_dir / 'prompts').exists()}")

        # Test with auto-discovery enabled
        loader = ConfigLoader(project_root=test_dir, enable_auto_discovery=True)

        # Debug: Check scanner
        print(f"\n  Auto-discovery enabled: {loader.enable_auto_discovery}")
        print(f"  Scanner available: {loader.scanner is not None}")

        config = loader.load()

        print(f"\n✓ Config loaded with auto-discovery")
        print(f"  Skills: {len(config.skills)}")
        print(f"  Commands: {len(config.commands)}")
        print(f"  Agents: {len(config.agents)}")
        print(f"  Prompts: {len(config.prompts)}")

        # Debug output
        print(f"\n  All skill names: {list(config.skills.keys())}")
        print(f"  All command names: {list(config.commands.keys())}")
        print(f"  All agent names: {list(config.agents.keys())}")
        print(f"  All prompt names: {list(config.prompts.keys())}")

        # Should discover our test resources
        assert "test-skill-1" in config.skills, "test-skill-1 not found in skills"
        assert "test-skill-2" in config.skills, "test-skill-2 not found in skills"
        assert "test-skill-3" in config.skills, "test-skill-3 not found in skills"

        assert "git-shortcuts" in config.commands, f"git-shortcuts not found. Available: {list(config.commands.keys())}"
        assert "docker-utils" in config.commands, f"docker-utils not found. Available: {list(config.commands.keys())}"

        assert "custom-explorer" in config.agents, f"custom-explorer not found. Available: {list(config.agents.keys())}"
        assert "code-analyzer" in config.agents, f"code-analyzer not found. Available: {list(config.agents.keys())}"

        assert "code-review" in config.prompts, f"code-review not found. Available: {list(config.prompts.keys())}"
        assert "api-doc" in config.prompts, f"api-doc not found. Available: {list(config.prompts.keys())}"

        print("\n  Discovered resources details:")
        for skill_name, skill_config in config.skills.items():
            if skill_name.startswith("test-"):
                print(f"    Skill: {skill_name} (priority: {skill_config.priority})")

        print("\n✅ ConfigLoader integration test PASSED")

    finally:
        shutil.rmtree(test_dir)


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("ResourceScanner Test Suite")
    print("Testing auto-discovery of Skills, Commands, Agents, Prompts")
    print("="*80)

    tests = [
        test_skill_detector,
        test_command_detector,
        test_agent_detector,
        test_prompt_detector,
        test_resource_scanner,
        test_integration_with_config_loader
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_func.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 All tests PASSED!")
    else:
        print(f"\n⚠️  {failed} test(s) FAILED")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
