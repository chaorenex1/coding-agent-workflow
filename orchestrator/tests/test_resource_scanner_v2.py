"""
Test suite for Resource Scanner V2

Tests hierarchical category support and different layout modes.
"""

import sys
import os
from pathlib import Path

# Windows encoding fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Simple test framework (pytest optional)
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    print("Note: pytest not installed, running simplified tests\n")

    # Mock pytest decorators
    class MockPytest:
        @staticmethod
        def fixture(func):
            return func

    pytest = MockPytest()

from orchestrator.core.resource_scanner_v2 import (
    ResourceScanner,
    ResourceLayout,
    ResourceCategory,
    CommandDetector,
    AgentDetector,
    PromptDetector,
    SkillDetector
)
from orchestrator.core.config_loader import ResourceType


class TestResourceScanner:
    """Test the main ResourceScanner class."""

    @pytest.fixture
    def base_path(self):
        """Return the actual project base path."""
        return project_root

    @pytest.fixture
    def scanner(self):
        """Create a ResourceScanner instance."""
        return ResourceScanner()

    def test_scanner_initialization(self, scanner):
        """Test scanner initializes correctly."""
        assert scanner is not None
        assert 'skills' in scanner.detectors
        assert 'commands' in scanner.detectors
        assert 'agents' in scanner.detectors
        assert 'prompts' in scanner.detectors

    def test_scan_all(self, scanner, base_path):
        """Test scanning all resource types."""
        results = scanner.scan_all(base_path, source="project")

        assert ResourceType.COMMAND in results
        assert ResourceType.AGENT in results
        assert ResourceType.SKILL in results
        assert ResourceType.PROMPT in results

        # Should find resources in each type
        assert len(results[ResourceType.COMMAND]) > 0, "Should find commands"
        assert len(results[ResourceType.AGENT]) > 0, "Should find agents"
        assert len(results[ResourceType.SKILL]) > 0, "Should find skills"
        assert len(results[ResourceType.PROMPT]) > 0, "Should find prompts"

        # Print summary
        print(f"\n=== Scan Results ===")
        for rt, resources in results.items():
            print(f"{rt.value}: {len(resources)} resources")
            for r in resources[:3]:  # Show first 3
                cat_str = f" (category: {r.category})" if r.category else ""
                print(f"  - {r.name}{cat_str}")

    def test_scan_commands_with_categories(self, scanner, base_path):
        """Test scanning commands with category detection."""
        commands = scanner.scan_type(base_path, ResourceType.COMMAND)

        assert len(commands) > 0, "Should find commands"

        # Check that categories are detected
        categorized = [c for c in commands if c.category is not None]
        assert len(categorized) > 0, "Should find categorized commands"

        # Print categories
        categories = set(c.category for c in commands if c.category)
        print(f"\n=== Command Categories ===")
        for cat in sorted(categories):
            cat_commands = [c for c in commands if c.category == cat]
            print(f"{cat}: {len(cat_commands)} commands")
            for cmd in cat_commands[:2]:
                print(f"  - {cmd.name}")

    def test_scan_agents_with_categories(self, scanner, base_path):
        """Test scanning agents with category detection."""
        agents = scanner.scan_type(base_path, ResourceType.AGENT)

        assert len(agents) > 0, "Should find agents"

        # Check that categories are detected
        categorized = [a for a in agents if a.category is not None]
        assert len(categorized) > 0, "Should find categorized agents"

        # Print categories
        categories = set(a.category for a in agents if a.category)
        print(f"\n=== Agent Categories ===")
        for cat in sorted(categories):
            cat_agents = [a for a in agents if a.category == cat]
            print(f"{cat}: {len(cat_agents)} agents")
            for agent in cat_agents[:2]:
                print(f"  - {agent.name}")

    def test_scan_skills_directory_based(self, scanner, base_path):
        """Test scanning skills with directory-based layout."""
        skills = scanner.scan_type(base_path, ResourceType.SKILL)

        assert len(skills) > 0, "Should find skills"

        # All skills should be directory-based
        for skill in skills:
            assert skill.layout == ResourceLayout.DIRECTORY_BASED
            assert skill.path.is_dir(), f"{skill.name} path should be a directory"

            # Should have marker file
            if skill.marker_file:
                assert skill.marker_file.exists(), f"{skill.name} should have SKILL.md"

        print(f"\n=== Skills Found ===")
        for skill in skills[:5]:
            print(f"  - {skill.name}: {skill.path.name}")
            if skill.entry_point:
                print(f"    Entry point: {skill.entry_point.name}")

    def test_scan_prompts_mixed_layout(self, scanner, base_path):
        """Test scanning prompts with mixed layout (flat and categorized)."""
        prompts = scanner.scan_type(base_path, ResourceType.PROMPT)

        assert len(prompts) > 0, "Should find prompts"

        # Check for both layouts
        flat = [p for p in prompts if p.layout == ResourceLayout.FLAT_FILE]
        categorized = [p for p in prompts if p.layout == ResourceLayout.CATEGORIZED_FILE]

        print(f"\n=== Prompts Layout ===")
        print(f"Flat: {len(flat)}")
        print(f"Categorized: {len(categorized)}")

        for prompt in prompts[:5]:
            cat_str = f" (category: {prompt.category})" if prompt.category else ""
            print(f"  - {prompt.name}{cat_str}")

    def test_get_categories(self, scanner, base_path):
        """Test getting categories for a resource type."""
        # Test command categories
        cmd_categories = scanner.get_categories(base_path, ResourceType.COMMAND)
        assert len(cmd_categories) > 0, "Should find command categories"

        print(f"\n=== Command Categories ===")
        for cat in cmd_categories:
            print(f"  - {cat.name}: {cat.display_name}")
            print(f"    Priority: {cat.priority}")

        # Test agent categories
        agent_categories = scanner.get_categories(base_path, ResourceType.AGENT)
        assert len(agent_categories) > 0, "Should find agent categories"

        print(f"\n=== Agent Categories ===")
        for cat in agent_categories:
            print(f"  - {cat.name}: {cat.display_name}")

    def test_scan_category(self, scanner, base_path):
        """Test scanning a specific category."""
        # Get all commands first
        all_commands = scanner.scan_type(base_path, ResourceType.COMMAND)
        categories = set(c.category for c in all_commands if c.category)

        if categories:
            # Test scanning first category
            test_category = sorted(categories)[0]
            category_commands = scanner.scan_category(
                base_path,
                ResourceType.COMMAND,
                test_category
            )

            assert len(category_commands) > 0, f"Should find commands in {test_category}"

            # All should belong to this category
            for cmd in category_commands:
                assert cmd.category == test_category

            print(f"\n=== Category: {test_category} ===")
            for cmd in category_commands:
                print(f"  - {cmd.name}")

    def test_get_resource_tree(self, scanner, base_path):
        """Test getting resource tree organized by category."""
        tree = scanner.get_resource_tree(base_path, ResourceType.COMMAND)

        assert tree is not None
        assert isinstance(tree, dict)

        print(f"\n=== Command Tree ===")
        for category, commands in sorted(tree.items(), key=lambda x: (x[0] is None, x[0])):
            cat_name = category if category else "(uncategorized)"
            print(f"{cat_name}: {len(commands)} commands")
            for cmd in commands[:2]:
                print(f"  - {cmd.name}")

    def test_convert_to_config(self, scanner, base_path):
        """Test converting discovered resources to config objects."""
        # Test with commands
        commands = scanner.scan_type(base_path, ResourceType.COMMAND)
        if commands:
            cmd = commands[0]
            config = scanner.convert_to_config(cmd)

            from orchestrator.core.config_loader import CommandConfig
            assert isinstance(config, CommandConfig)
            assert config.name == cmd.name

        # Test with skills
        skills = scanner.scan_type(base_path, ResourceType.SKILL)
        if skills:
            skill = skills[0]
            config = scanner.convert_to_config(skill)

            from orchestrator.core.config_loader import SkillConfig
            assert isinstance(config, SkillConfig)
            assert config.name == skill.name


class TestDetectors:
    """Test individual detector classes."""

    @pytest.fixture
    def base_path(self):
        return project_root

    def test_command_detector(self, base_path):
        """Test CommandDetector."""
        detector = CommandDetector(source="project")

        assert detector.LAYOUT == ResourceLayout.CATEGORIZED_FILE
        assert detector.MAX_DEPTH == 2
        assert detector.get_resource_type() == ResourceType.COMMAND

        commands_dir = base_path / "commands"
        if commands_dir.exists():
            results = detector.scan_directory(commands_dir)
            assert len(results) > 0, "Should find commands"

            # All should be commands
            for r in results:
                assert r.resource_type == ResourceType.COMMAND

            print(f"\n=== CommandDetector Results ===")
            for cmd in results[:5]:
                print(f"  - {cmd.name} (category: {cmd.category})")

    def test_agent_detector(self, base_path):
        """Test AgentDetector."""
        detector = AgentDetector(source="project")

        assert detector.LAYOUT == ResourceLayout.CATEGORIZED_FILE
        assert detector.MAX_DEPTH == 2
        assert detector.get_resource_type() == ResourceType.AGENT

        agents_dir = base_path / "agents"
        if agents_dir.exists():
            results = detector.scan_directory(agents_dir)
            assert len(results) > 0, "Should find agents"

            # All should be agents
            for r in results:
                assert r.resource_type == ResourceType.AGENT

            print(f"\n=== AgentDetector Results ===")
            for agent in results[:5]:
                print(f"  - {agent.name} (category: {agent.category})")

    def test_skill_detector(self, base_path):
        """Test SkillDetector."""
        detector = SkillDetector(source="project")

        assert detector.LAYOUT == ResourceLayout.DIRECTORY_BASED
        assert detector.MAX_DEPTH == 1
        assert detector.get_resource_type() == ResourceType.SKILL

        skills_dir = base_path / "skills"
        if skills_dir.exists():
            results = detector.scan_directory(skills_dir)
            assert len(results) > 0, "Should find skills"

            # All should be skills
            for r in results:
                assert r.resource_type == ResourceType.SKILL
                assert r.layout == ResourceLayout.DIRECTORY_BASED

            print(f"\n=== SkillDetector Results ===")
            for skill in results[:5]:
                print(f"  - {skill.name}")
                print(f"    Path: {skill.path.name}")
                print(f"    Entry: {skill.entry_point.name if skill.entry_point else 'None'}")

    def test_prompt_detector(self, base_path):
        """Test PromptDetector."""
        detector = PromptDetector(source="project")

        assert detector.MAX_DEPTH == 2
        assert detector.get_resource_type() == ResourceType.PROMPT

        prompts_dir = base_path / "prompts"
        if prompts_dir.exists():
            results = detector.scan_directory(prompts_dir)
            assert len(results) > 0, "Should find prompts"

            # All should be prompts
            for r in results:
                assert r.resource_type == ResourceType.PROMPT

            print(f"\n=== PromptDetector Results ===")
            for prompt in results[:5]:
                layout_str = prompt.layout.value if prompt.layout else "unknown"
                cat_str = f" (category: {prompt.category})" if prompt.category else ""
                print(f"  - {prompt.name} [{layout_str}]{cat_str}")


class TestResourceCategory:
    """Test ResourceCategory class."""

    def test_from_directory_name(self):
        """Test creating category from directory name."""
        cat = ResourceCategory.from_directory_name("project-analyzer")
        assert cat.name == "project-analyzer"
        assert cat.display_name == "Project Analyzer"

        cat2 = ResourceCategory.from_directory_name("quick_code")
        assert cat2.name == "quick_code"
        assert cat2.display_name == "Quick Code"


class TestIntegration:
    """Integration tests with real project structure."""

    @pytest.fixture
    def scanner(self):
        return ResourceScanner()

    @pytest.fixture
    def base_path(self):
        return project_root

    def test_full_scan_workflow(self, scanner, base_path):
        """Test complete scanning workflow."""
        print("\n" + "="*60)
        print("FULL SCAN WORKFLOW TEST")
        print("="*60)

        # Step 1: Scan all resources
        all_resources = scanner.scan_all(base_path)

        # Step 2: Get categories for each type
        for resource_type in [ResourceType.COMMAND, ResourceType.AGENT, ResourceType.SKILL]:
            categories = scanner.get_categories(base_path, resource_type)
            print(f"\n{resource_type.value} categories: {len(categories)}")
            for cat in categories[:3]:
                print(f"  - {cat.display_name}")

        # Step 3: Get resource tree
        for resource_type in [ResourceType.COMMAND, ResourceType.AGENT]:
            tree = scanner.get_resource_tree(base_path, resource_type)
            print(f"\n{resource_type.value} tree:")
            for cat_name, resources in sorted(tree.items(), key=lambda x: (x[0] is None, x[0]))[:3]:
                cat_str = cat_name if cat_name else "(uncategorized)"
                print(f"  {cat_str}: {len(resources)} resources")

        # Step 4: Convert to configs
        commands = all_resources[ResourceType.COMMAND]
        if commands:
            config = scanner.convert_to_config(commands[0])
            print(f"\nSample config conversion: {config.name}")

        print("\n" + "="*60)


def test_specific_resources():
    """Test scanning specific known resources."""
    scanner = ResourceScanner()
    base_path = project_root

    print("\n" + "="*60)
    print("SPECIFIC RESOURCE TESTS")
    print("="*60)

    # Test known command
    commands = scanner.scan_type(base_path, ResourceType.COMMAND)
    code_reader = next((c for c in commands if c.name == "code-reader"), None)
    if code_reader:
        print(f"\n✓ Found code-reader command")
        print(f"  Category: {code_reader.category}")
        print(f"  Layout: {code_reader.layout.value}")
        assert code_reader.category == "project-analyzer"

    # Test known agent
    agents = scanner.scan_type(base_path, ResourceType.AGENT)
    req_agent = next((a for a in agents if "requirement-analysis" in a.name), None)
    if req_agent:
        print(f"\n✓ Found requirement-analysis-agent")
        print(f"  Category: {req_agent.category}")
        print(f"  Layout: {req_agent.layout.value}")

    # Test known skill
    skills = scanner.scan_type(base_path, ResourceType.SKILL)
    bridge_skill = next((s for s in skills if "codex-cli-bridge" in s.name), None)
    if bridge_skill:
        print(f"\n✓ Found codex-cli-bridge skill")
        print(f"  Layout: {bridge_skill.layout.value}")
        print(f"  Has entry point: {bridge_skill.entry_point is not None}")
        assert bridge_skill.layout == ResourceLayout.DIRECTORY_BASED

    print("\n" + "="*60)


if __name__ == "__main__":
    print("Running Resource Scanner V2 Tests...\n")

    # Run specific resource tests first
    test_specific_resources()

    # Run class-based tests manually if pytest not available
    if not HAS_PYTEST:
        print("\nRunning manual tests (pytest not available)...\n")

        # Test ResourceScanner
        print("="*60)
        print("Testing ResourceScanner")
        print("="*60)

        scanner = ResourceScanner()
        base = project_root

        test_scanner = TestResourceScanner()
        test_scanner.test_scanner_initialization(scanner)
        print("✓ Scanner initialization test passed")

        test_scanner.test_scan_all(scanner, base)
        print("✓ Scan all test passed")

        test_scanner.test_scan_commands_with_categories(scanner, base)
        print("✓ Scan commands with categories test passed")

        test_scanner.test_scan_agents_with_categories(scanner, base)
        print("✓ Scan agents with categories test passed")

        test_scanner.test_scan_skills_directory_based(scanner, base)
        print("✓ Scan skills test passed")

        test_scanner.test_scan_prompts_mixed_layout(scanner, base)
        print("✓ Scan prompts test passed")

        test_scanner.test_get_categories(scanner, base)
        print("✓ Get categories test passed")

        test_scanner.test_scan_category(scanner, base)
        print("✓ Scan category test passed")

        test_scanner.test_get_resource_tree(scanner, base)
        print("✓ Get resource tree test passed")

        test_scanner.test_convert_to_config(scanner, base)
        print("✓ Convert to config test passed")

        # Test Detectors
        print("\n" + "="*60)
        print("Testing Detectors")
        print("="*60)

        test_detectors = TestDetectors()
        test_detectors.test_command_detector(base)
        print("✓ CommandDetector test passed")

        test_detectors.test_agent_detector(base)
        print("✓ AgentDetector test passed")

        test_detectors.test_skill_detector(base)
        print("✓ SkillDetector test passed")

        test_detectors.test_prompt_detector(base)
        print("✓ PromptDetector test passed")

        # Test ResourceCategory
        print("\n" + "="*60)
        print("Testing ResourceCategory")
        print("="*60)

        test_cat = TestResourceCategory()
        test_cat.test_from_directory_name()
        print("✓ ResourceCategory test passed")

        # Integration tests
        print("\n" + "="*60)
        print("Testing Integration")
        print("="*60)

        test_integration = TestIntegration()
        test_integration.test_full_scan_workflow(scanner, base)
        print("✓ Integration test passed")

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
    else:
        # Run pytest
        pytest.main([__file__, "-v", "-s"])
