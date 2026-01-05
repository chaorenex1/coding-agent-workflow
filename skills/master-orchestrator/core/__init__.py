"""
Orchestrator Core Module - 核心组件包

提供统一的公共API接口，方便其他模块导入使用。
"""

# Backend Orchestrator - 后端协调器
from .backend_orchestrator import (
    BackendOrchestrator,
    TaskResult,
    ComparisonResult,
    PipelineResult
)

# Event Parser - 事件解析器
from .event_parser import (
    EventStream,
    ParsedEvent,
    MemexEventParser
)

# Configuration System - 配置系统
from .config_loader import (
    ConfigLoader,
    OrchestratorConfig,
    ResourceType,
    SkillConfig,
    CommandConfig,
    AgentConfig,
    PromptConfig,
    ParallelConfig,
    SlashCommandConfig
)

# Unified Registry - 统一资源注册表
from .unified_registry import (
    UnifiedRegistry,
    ResourceMetadata,
    create_registry_from_config
)

# Executor Factory - 执行器工厂
from .executor_factory import (
    ExecutorFactory,
    YAMLSkillExecutor,  # 向后兼容别名
    MarkdownSkillExecutor,  # 推荐使用
    CommandExecutorAdapter,
    AgentExecutorAdapter,
    PromptExecutorAdapter
)

# Resource Content Parser - 资源内容解析器
from .resource_content_parser import (
    ResourceContentParser,
    MarkdownResourceParser,
    YAMLResourceParser,
    ParsedResourceContent,
    get_parser
)

# Dependency Analyzer - 依赖分析器
from .dependency_analyzer import (
    DependencyAnalyzer,
    Task,
    ParallelGroup,
    CyclicDependencyError
)

# Parallel Scheduler - 并行调度器
from .parallel_scheduler import (
    ParallelScheduler,
    TaskResult as SchedulerTaskResult,
    BatchResult
)

# Slash Command System - Slash命令系统
from .slash_command import (
    SlashCommandType,
    SlashCommandMetadata,
    SlashCommandResult,
    SlashCommandHandler,
    SystemCommandHandler,
    ShellCommandHandler,
    SkillCommandHandler,
    AgentCommandHandler,
    PromptCommandHandler
)

# Slash Command Registry - Slash命令注册表
from .slash_command_registry import (
    SlashCommandRegistry,
    register_builtin_commands
)

# Resource Scanner V1 - 资源扫描器（向后兼容）
from .resource_scanner import (
    ResourceScanner as ResourceScannerV1,
    DiscoveredResource as DiscoveredResourceV1,
    BaseResourceDetector as BaseResourceDetectorV1,
    SkillDetector as SkillDetectorV1,
    CommandDetector as CommandDetectorV1,
    AgentDetector as AgentDetectorV1,
    PromptDetector as PromptDetectorV1
)

# Resource Scanner V2 - 增强版资源扫描器（默认）
from .resource_scanner_v2 import (
    ResourceScanner,  # V2 is now the default
    DiscoveredResource,  # V2 is now the default
    BaseResourceDetector,
    SkillDetector,
    CommandDetector,
    AgentDetector,
    PromptDetector,
    ResourceLayout,
    ResourceCategory
)

# Log Manager - 日志管理器
from .log_manager import LogManager

# Registry Persistence - 注册表持久化
from .registry_persistence import RegistryPersistence

# Temp File Manager - 临时文件管理器
from .temp_file_manager import TempFileManager

__all__ = [
    # Backend Orchestrator
    'BackendOrchestrator',
    'TaskResult',
    'ComparisonResult',
    'PipelineResult',

    # Event Parser
    'EventStream',
    'ParsedEvent',
    'MemexEventParser',

    # Configuration
    'ConfigLoader',
    'OrchestratorConfig',
    'ResourceType',
    'SkillConfig',
    'CommandConfig',
    'AgentConfig',
    'PromptConfig',
    'ParallelConfig',
    'SlashCommandConfig',

    # Registry
    'UnifiedRegistry',
    'ResourceMetadata',
    'create_registry_from_config',

    # Executor Factory
    'ExecutorFactory',
    'YAMLSkillExecutor',
    'CommandExecutorAdapter',
    'AgentExecutorAdapter',
    'PromptExecutorAdapter',

    # Dependency Analyzer
    'DependencyAnalyzer',
    'Task',
    'ParallelGroup',
    'CyclicDependencyError',

    # Parallel Scheduler
    'ParallelScheduler',
    'SchedulerTaskResult',
    'BatchResult',

    # Slash Commands
    'SlashCommandType',
    'SlashCommandMetadata',
    'SlashCommandResult',
    'SlashCommandHandler',
    'SystemCommandHandler',
    'ShellCommandHandler',
    'SkillCommandHandler',
    'AgentCommandHandler',
    'PromptCommandHandler',
    'SlashCommandRegistry',
    'register_builtin_commands',

    # Resource Scanner (V2 is default)
    'ResourceScanner',  # V2
    'DiscoveredResource',  # V2
    'BaseResourceDetector',  # V2
    'SkillDetector',  # V2
    'CommandDetector',  # V2
    'AgentDetector',  # V2
    'PromptDetector',  # V2
    'ResourceLayout',  # V2
    'ResourceCategory',  # V2

    # Resource Scanner V1 (backward compatibility)
    'ResourceScannerV1',
    'DiscoveredResourceV1',
    'BaseResourceDetectorV1',
    'SkillDetectorV1',
    'CommandDetectorV1',
    'AgentDetectorV1',
    'PromptDetectorV1',

    # Log Manager
    'LogManager',

    # Registry Persistence
    'RegistryPersistence',

    # Temp File Manager
    'TempFileManager',
]
