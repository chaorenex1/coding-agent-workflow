#!/usr/bin/env python3
"""
SkillRegistry - 技能注册和管理系统

功能：
- 技能自动注册和发现
- 元数据管理
- 依赖检查
- 版本控制
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class SkillCategory(Enum):
    """技能类别"""
    DEVELOPMENT = "development"
    UX_DESIGN = "ux_design"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    TESTING = "testing"
    DOCUMENTATION = "documentation"


@dataclass
class SkillMetadata:
    """技能元数据"""
    name: str
    category: SkillCategory
    description: str
    version: str
    author: str
    backends_required: List[str]  # 需要的后端：claude, gemini, codex
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    entry_point: Optional[str] = None  # 入口文件路径

    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data["category"] = self.category.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "SkillMetadata":
        """从字典创建"""
        data["category"] = SkillCategory(data["category"])
        return cls(**data)


class SkillRegistry:
    """
    技能注册表

    管理所有可用技能的注册、查询和验证
    """

    def __init__(self, skills_dir: Optional[Path] = None):
        """
        初始化技能注册表

        Args:
            skills_dir: 技能目录，默认为 ./skills
        """
        if skills_dir is None:
            skills_dir = Path(__file__).parent
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, SkillMetadata] = {}
        self._load_skills()

    def _load_skills(self):
        """从技能目录加载所有技能"""
        if not self.skills_dir.exists():
            return

        # 遍历技能目录
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            # 查找 SKILL.md 文件
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            # 尝试解析元数据
            metadata = self._parse_skill_metadata(skill_dir, skill_md)
            if metadata:
                self.skills[metadata.name] = metadata

    def _parse_skill_metadata(self, skill_dir: Path, skill_md: Path) -> Optional[SkillMetadata]:
        """
        从 SKILL.md 解析技能元数据

        Args:
            skill_dir: 技能目录
            skill_md: SKILL.md 文件路径

        Returns:
            SkillMetadata 或 None
        """
        try:
            content = skill_md.read_text(encoding='utf-8')

            # 简单的元数据提取（从 YAML frontmatter 或特定标记）
            # 这里使用简化版本，实际可以使用 YAML 解析
            metadata = self._extract_metadata_from_markdown(skill_dir, content)
            return metadata

        except Exception as e:
            print(f"Warning: Failed to parse {skill_md}: {e}")
            return None

    def _extract_metadata_from_markdown(self, skill_dir: Path, content: str) -> Optional[SkillMetadata]:
        """
        从 Markdown 内容提取元数据

        Args:
            skill_dir: 技能目录
            content: Markdown 内容

        Returns:
            SkillMetadata 或 None
        """
        # 提取标题作为名称
        lines = content.split('\n')
        name = None
        description = None

        for line in lines:
            if line.startswith('# '):
                name = line[2:].strip()
                break

        if not name:
            return None

        # 提取描述（第一个非标题段落）
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('#') and not line.startswith('```'):
                description = line.strip()
                break

        # 根据技能名称推断类别和后端
        category = self._infer_category(name, skill_dir.name)
        backends = self._infer_backends(name, skill_dir.name)

        # 查找入口点
        entry_point = self._find_entry_point(skill_dir)

        return SkillMetadata(
            name=name,
            category=category,
            description=description or "No description",
            version="1.0.0",
            author="Unknown",
            backends_required=backends,
            dependencies=[],
            entry_point=str(entry_point.relative_to(skill_dir)) if entry_point else None
        )

    def _infer_category(self, name: str, dirname: str) -> SkillCategory:
        """推断技能类别"""
        name_lower = name.lower() + " " + dirname.lower()

        if "dev" in name_lower or "workflow" in name_lower:
            return SkillCategory.DEVELOPMENT
        elif "ux" in name_lower or "design" in name_lower:
            return SkillCategory.UX_DESIGN
        elif "code" in name_lower or "codex" in name_lower:
            return SkillCategory.CODE_GENERATION
        elif "test" in name_lower:
            return SkillCategory.TESTING
        elif "doc" in name_lower:
            return SkillCategory.DOCUMENTATION
        else:
            return SkillCategory.ANALYSIS

    def _infer_backends(self, name: str, dirname: str) -> List[str]:
        """推断需要的后端"""
        name_lower = name.lower() + " " + dirname.lower()
        backends = []

        if "claude" in name_lower:
            backends.append("claude")
        if "gemini" in name_lower or "ux" in name_lower:
            backends.append("gemini")
        if "codex" in name_lower or "code" in name_lower:
            backends.append("codex")

        # 默认
        if not backends:
            backends = ["claude"]

        return backends

    def _find_entry_point(self, skill_dir: Path) -> Optional[Path]:
        """查找技能入口点"""
        # 常见入口点文件名
        entry_candidates = [
            "auto_workflow.py",
            "main.py",
            "skill.py",
            "__init__.py"
        ]

        for candidate in entry_candidates:
            entry_file = skill_dir / candidate
            if entry_file.exists():
                return entry_file

        # 检查 scripts 子目录
        scripts_dir = skill_dir / "scripts"
        if scripts_dir.exists():
            for candidate in entry_candidates:
                entry_file = scripts_dir / candidate
                if entry_file.exists():
                    return entry_file

        return None

    def register_skill(self, metadata: SkillMetadata):
        """
        注册技能

        Args:
            metadata: 技能元数据
        """
        self.skills[metadata.name] = metadata

    def get_skill(self, name: str) -> Optional[SkillMetadata]:
        """
        获取技能元数据

        Args:
            name: 技能名称

        Returns:
            SkillMetadata 或 None
        """
        return self.skills.get(name)

    def list_skills(self, category: Optional[SkillCategory] = None) -> List[SkillMetadata]:
        """
        列出技能

        Args:
            category: 可选的类别筛选

        Returns:
            技能列表
        """
        if category:
            return [s for s in self.skills.values() if s.category == category]
        return list(self.skills.values())

    def search_skills(self, keyword: str) -> List[SkillMetadata]:
        """
        搜索技能

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的技能列表
        """
        results = []
        keyword_lower = keyword.lower()

        for skill in self.skills.values():
            if (keyword_lower in skill.name.lower() or
                keyword_lower in skill.description.lower()):
                results.append(skill)

        return results

    def check_dependencies(self, skill_name: str) -> Tuple[bool, List[str]]:
        """
        检查技能依赖是否满足

        Args:
            skill_name: 技能名称

        Returns:
            (是否满足, 缺失的依赖列表)
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return False, [f"Skill '{skill_name}' not found"]

        missing = []

        # 检查后端依赖
        for backend in skill.backends_required:
            # 这里简化检查，实际应检查 memex-cli 是否支持该后端
            if backend not in ["claude", "gemini", "codex"]:
                missing.append(f"Unknown backend: {backend}")

        # 检查其他依赖
        for dep in skill.dependencies:
            dep_skill = self.get_skill(dep)
            if not dep_skill:
                missing.append(f"Dependency skill not found: {dep}")

        return len(missing) == 0, missing

    def get_categories(self) -> List[SkillCategory]:
        """获取所有类别"""
        return list(set(s.category for s in self.skills.values()))

    def export_registry(self, output_path: Path):
        """
        导出注册表为 JSON

        Args:
            output_path: 输出文件路径
        """
        data = {
            "skills": {name: skill.to_dict() for name, skill in self.skills.items()}
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def import_registry(self, input_path: Path):
        """
        从 JSON 导入注册表

        Args:
            input_path: 输入文件路径
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for name, skill_data in data.get("skills", {}).items():
            metadata = SkillMetadata.from_dict(skill_data)
            self.register_skill(metadata)


# 使用示例
if __name__ == "__main__":
    import sys

    registry = SkillRegistry()

    print(f"[SkillRegistry] 已加载 {len(registry.skills)} 个技能\n")

    # 列出所有技能
    print("所有技能：")
    for skill in registry.list_skills():
        print(f"  - {skill.name}")
        print(f"    类别: {skill.category.value}")
        print(f"    描述: {skill.description}")
        print(f"    后端: {', '.join(skill.backends_required)}")
        if skill.entry_point:
            print(f"    入口: {skill.entry_point}")
        print()

    # 搜索示例
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        print(f"\n搜索 '{keyword}':")
        results = registry.search_skills(keyword)
        for skill in results:
            print(f"  - {skill.name}: {skill.description}")

    # 导出注册表
    output_file = Path(__file__).parent / "skill_registry.json"
    registry.export_registry(output_file)
    print(f"\n[OK] 注册表已导出到: {output_file}")
