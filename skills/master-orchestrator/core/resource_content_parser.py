#!/usr/bin/env python3
"""
资源内容解析器

提供统一的资源内容解析接口，支持多种格式（Markdown, YAML, JSON等）。
"""

import re
import yaml
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import logging


logger = logging.getLogger(__name__)


@dataclass
class ParsedResourceContent:
    """
    解析后的资源内容

    Attributes:
        metadata: 元数据（description, enabled, priority等）
        sections: 章节内容（如 System Prompt, User Prompt Template）
        raw_content: 原始文件内容
        file_path: 文件路径
    """
    metadata: Dict[str, Any] = field(default_factory=dict)
    sections: Dict[str, str] = field(default_factory=dict)
    raw_content: str = ""
    file_path: Optional[Path] = None

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取元数据字段"""
        return self.metadata.get(key, default)

    def get_section(self, section_name: str, default: str = "") -> str:
        """获取章节内容"""
        return self.sections.get(section_name, default)

    def has_section(self, section_name: str) -> bool:
        """检查是否存在指定章节"""
        return section_name in self.sections

    def list_sections(self) -> List[str]:
        """列出所有章节名称"""
        return list(self.sections.keys())


class ResourceContentParser(ABC):
    """
    资源内容解析器基类

    定义统一的解析接口，子类实现具体格式的解析逻辑。
    """

    @abstractmethod
    def parse(self, file_path: Path) -> ParsedResourceContent:
        """
        解析资源文件

        Args:
            file_path: 资源文件路径

        Returns:
            ParsedResourceContent: 解析结果

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 解析失败
        """
        pass

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """
        检查是否支持解析该文件

        Args:
            file_path: 文件路径

        Returns:
            bool: 是否支持
        """
        pass


class MarkdownResourceParser(ResourceContentParser):
    """
    Markdown 资源解析器

    支持的格式：
    ```markdown
    # resource-name

    description: Resource description
    enabled: true
    priority: 80
    backend: claude
    tags: [tag1, tag2]

    ## Section 1

    Section content...

    ## Section 2

    More content...
    ```

    元数据格式支持：
    1. 键值对（key: value）- 放在 # 标题后、第一个 ## 章节前
    2. YAML front matter（可选，--- 包裹）
    """

    def can_parse(self, file_path: Path) -> bool:
        """检查是否为 Markdown 文件"""
        return file_path.suffix.lower() in ['.md', '.markdown']

    def parse(self, file_path: Path) -> ParsedResourceContent:
        """
        解析 Markdown 资源文件

        Args:
            file_path: Markdown 文件路径

        Returns:
            ParsedResourceContent: 解析结果
        """
        if not file_path.exists():
            raise FileNotFoundError(f"资源文件不存在: {file_path}")

        if not self.can_parse(file_path):
            raise ValueError(f"不支持的文件格式: {file_path.suffix}")

        try:
            # 读取文件
            raw_content = file_path.read_text(encoding='utf-8')

            # 解析元数据
            metadata = self._parse_metadata(raw_content)

            # 解析章节
            sections = self._parse_sections(raw_content)

            return ParsedResourceContent(
                metadata=metadata,
                sections=sections,
                raw_content=raw_content,
                file_path=file_path
            )

        except Exception as e:
            logger.error(f"解析 Markdown 文件失败: {file_path}, 错误: {e}")
            raise ValueError(f"解析失败: {e}")

    def _parse_metadata(self, content: str) -> Dict[str, Any]:
        """
        解析元数据

        支持两种格式：
        1. YAML front matter (优先)
        2. 键值对（key: value 格式，位于 # 标题后）
        """
        metadata = {}

        # 方法 1: 尝试解析 YAML front matter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    front_matter = yaml.safe_load(parts[1])
                    if front_matter and isinstance(front_matter, dict):
                        metadata.update(front_matter)
                        logger.debug("从 YAML front matter 提取元数据")
                        return metadata
                except Exception as e:
                    logger.warning(f"解析 YAML front matter 失败: {e}")

        # 方法 2: 提取键值对元数据
        # 位置：# 标题后，第一个 ## 章节前
        lines = content.split('\n')
        in_metadata_section = False
        metadata_started = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # 跳过第一个 # 标题
            if stripped.startswith('# ') and not metadata_started:
                in_metadata_section = True
                metadata_started = True
                # 从标题提取 name（如果元数据中没有）
                if 'name' not in metadata:
                    metadata['name'] = stripped[2:].strip()
                continue

            # 遇到 ## 章节，结束元数据提取
            if stripped.startswith('## '):
                break

            # 在元数据区域内
            if in_metadata_section and stripped:
                # 解析 key: value 格式
                if ':' in stripped and not stripped.startswith('#'):
                    key, value = stripped.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    # 类型转换
                    metadata[key] = self._parse_value(value)

        return metadata

    def _parse_value(self, value: str) -> Any:
        """
        解析值的类型

        支持：
        - bool: true/false
        - int: 123
        - list: [item1, item2]
        - str: 其他情况
        """
        value = value.strip()

        # Boolean
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False

        # List (简单格式: [item1, item2])
        if value.startswith('[') and value.endswith(']'):
            items_str = value[1:-1]
            items = [item.strip().strip('"').strip("'") for item in items_str.split(',')]
            return [item for item in items if item]

        # Integer
        try:
            return int(value)
        except ValueError:
            pass

        # Float
        try:
            return float(value)
        except ValueError:
            pass

        # String (去除引号)
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]

        return value

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """
        解析 Markdown 章节

        识别 ## 标题，提取章节内容
        """
        sections = {}
        current_section = None
        current_content = []

        lines = content.split('\n')
        skip_until_section = True  # 跳过元数据区域

        for line in lines:
            stripped = line.strip()

            # 识别 ## 章节标题
            if stripped.startswith('## '):
                skip_until_section = False

                # 保存上一个章节
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                # 开始新章节
                current_section = stripped[3:].strip()
                current_content = []

            # 章节内容
            elif not skip_until_section and current_section:
                current_content.append(line)

        # 保存最后一个章节
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections


class YAMLResourceParser(ResourceContentParser):
    """
    YAML 资源解析器（预留，未来实现）
    """

    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in ['.yaml', '.yml']

    def parse(self, file_path: Path) -> ParsedResourceContent:
        """解析 YAML 文件"""
        if not file_path.exists():
            raise FileNotFoundError(f"资源文件不存在: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                raise ValueError("YAML 文件根元素必须是字典")

            return ParsedResourceContent(
                metadata=data,
                sections={},
                raw_content=file_path.read_text(encoding='utf-8'),
                file_path=file_path
            )

        except Exception as e:
            logger.error(f"解析 YAML 文件失败: {file_path}, 错误: {e}")
            raise ValueError(f"解析失败: {e}")


# 解析器工厂
def get_parser(file_path: Path) -> ResourceContentParser:
    """
    根据文件扩展名获取合适的解析器

    Args:
        file_path: 文件路径

    Returns:
        ResourceContentParser: 解析器实例

    Raises:
        ValueError: 不支持的文件格式
    """
    parsers = [
        MarkdownResourceParser(),
        YAMLResourceParser()
    ]

    for parser in parsers:
        if parser.can_parse(file_path):
            return parser

    raise ValueError(f"不支持的文件格式: {file_path.suffix}")
