"""
Slash Command Registry for managing and executing slash commands.

Provides:
- Command registration and discovery
- Priority-based override
- Command execution with proper handler routing
- Command listing and search
"""

from typing import Dict, List, Optional, Any
import logging

from .slash_command import (
    SlashCommandMetadata, SlashCommandResult, SlashCommandType,
    get_handler, SlashCommandHandler
)

logger = logging.getLogger(__name__)


class SlashCommandRegistry:
    """
    Registry for managing slash commands.

    Features:
    - Register commands from multiple sources (builtin, user, project)
    - Priority-based override (higher priority wins)
    - Execute commands with appropriate handlers
    - List and search commands
    """

    def __init__(self, orchestrator=None):
        """
        Initialize slash command registry.

        Args:
            orchestrator: MasterOrchestrator instance (for handler access)
        """
        self.orchestrator = orchestrator
        self._commands: Dict[str, SlashCommandMetadata] = {}
        self._handlers: Dict[SlashCommandType, SlashCommandHandler] = {}

        logger.debug("SlashCommandRegistry initialized")

    def register(self, command: SlashCommandMetadata, overwrite: bool = False) -> bool:
        """
        Register a slash command.

        Commands with higher priority override lower priority commands
        with the same name.

        Args:
            command: Command metadata to register
            overwrite: If True, always overwrite existing command

        Returns:
            True if registered (or overrode existing), False if skipped
        """
        name = command.name

        if name in self._commands:
            existing = self._commands[name]

            if not overwrite:
                # Priority-based override
                if command.priority > existing.priority:
                    logger.info(f"Overriding command '{name}': "
                               f"{existing.source}(p={existing.priority}) → "
                               f"{command.source}(p={command.priority})")
                    self._commands[name] = command
                    return True
                else:
                    logger.debug(f"Skipping lower priority command '{name}': "
                                f"{command.source}(p={command.priority}) < "
                                f"{existing.source}(p={existing.priority})")
                    return False
            else:
                logger.info(f"Force overwriting command '{name}'")
                self._commands[name] = command
                return True
        else:
            logger.debug(f"Registering new command '{name}' "
                        f"({command.type.value}, source={command.source})")
            self._commands[name] = command
            return True

    def get(self, name: str) -> Optional[SlashCommandMetadata]:
        """
        Get command by name (without slash).

        Args:
            name: Command name (e.g., "discover", not "/discover")

        Returns:
            Command metadata if found, None otherwise
        """
        return self._commands.get(name)

    def exists(self, name: str) -> bool:
        """
        Check if command exists.

        Args:
            name: Command name (without slash)

        Returns:
            True if command exists
        """
        return name in self._commands

    def list_commands(
        self,
        type_filter: Optional[SlashCommandType] = None,
        source_filter: Optional[str] = None,
        enabled_only: bool = True
    ) -> List[SlashCommandMetadata]:
        """
        List all registered commands.

        Args:
            type_filter: Filter by command type
            source_filter: Filter by source (builtin/user/project)
            enabled_only: Only return enabled commands

        Returns:
            List of command metadata
        """
        commands = list(self._commands.values())

        # Apply filters
        if type_filter:
            commands = [c for c in commands if c.type == type_filter]

        if source_filter:
            commands = [c for c in commands if c.source == source_filter]

        if enabled_only:
            commands = [c for c in commands if c.enabled]

        # Sort by priority (descending) then name
        commands.sort(key=lambda c: (-c.priority, c.name))

        return commands

    def execute(
        self,
        command_name: str,
        args: Optional[List[str]] = None,
        **kwargs
    ) -> SlashCommandResult:
        """
        Execute a slash command.

        Args:
            command_name: Command name (with or without slash)
            args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            SlashCommandResult
        """
        # Remove leading slash if present
        if command_name.startswith('/'):
            command_name = command_name[1:]

        # Get command metadata
        command = self.get(command_name)
        if not command:
            return SlashCommandResult(
                command=f"/{command_name}",
                success=False,
                error=f"Command '/{command_name}' not found"
            )

        if not command.enabled:
            return SlashCommandResult(
                command=f"/{command_name}",
                success=False,
                error=f"Command '/{command_name}' is disabled"
            )

        # Get or create handler
        handler = self._get_handler(command.type)

        # Execute command
        try:
            logger.info(f"Executing command: /{command_name} (type={command.type.value})")
            result = handler.execute(command, args or [], kwargs)
            logger.info(f"Command /{command_name} completed: "
                       f"success={result.success}, duration={result.duration_seconds:.3f}s")
            return result

        except Exception as e:
            logger.error(f"Command /{command_name} failed with exception: {e}")
            return SlashCommandResult(
                command=f"/{command_name}",
                success=False,
                error=f"Execution failed: {str(e)}"
            )

    def _get_handler(self, command_type: SlashCommandType) -> SlashCommandHandler:
        """
        Get or create handler for command type.

        Args:
            command_type: Type of command

        Returns:
            Handler instance
        """
        if command_type not in self._handlers:
            self._handlers[command_type] = get_handler(command_type, self.orchestrator)

        return self._handlers[command_type]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dictionary with statistics
        """
        commands = list(self._commands.values())

        by_type = {}
        by_source = {}
        enabled_count = 0

        for cmd in commands:
            # Count by type
            type_name = cmd.type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1

            # Count by source
            by_source[cmd.source] = by_source.get(cmd.source, 0) + 1

            # Count enabled
            if cmd.enabled:
                enabled_count += 1

        return {
            "total_commands": len(commands),
            "enabled_commands": enabled_count,
            "disabled_commands": len(commands) - enabled_count,
            "by_type": by_type,
            "by_source": by_source
        }

    def clear(self):
        """Clear all registered commands."""
        self._commands.clear()
        self._handlers.clear()
        logger.info("Slash command registry cleared")

    def __len__(self) -> int:
        """Get number of registered commands."""
        return len(self._commands)

    def __repr__(self) -> str:
        return f"SlashCommandRegistry({len(self)} commands)"


def register_builtin_commands(registry: SlashCommandRegistry):
    """
    Register built-in system commands.

    Args:
        registry: SlashCommandRegistry to register commands to
    """
    builtin_commands = [
        # System commands
        SlashCommandMetadata(
            name="discover",
            type=SlashCommandType.SYSTEM,
            description="Auto-discover and register resources",
            handler="_auto_discover",
            enabled=True,
            priority=100,
            source="builtin",
            examples=["/discover"]
        ),

        SlashCommandMetadata(
            name="list-skills",
            type=SlashCommandType.SYSTEM,
            description="List all registered skills",
            handler="_list_skills",
            enabled=True,
            priority=100,
            source="builtin",
            examples=["/list-skills"]
        ),

        SlashCommandMetadata(
            name="list-commands",
            type=SlashCommandType.SYSTEM,
            description="List all registered slash commands",
            handler="_list_slash_commands",
            enabled=True,
            priority=100,
            source="builtin",
            examples=["/list-commands"]
        ),

        SlashCommandMetadata(
            name="reload",
            type=SlashCommandType.SYSTEM,
            description="Reload configuration",
            handler="_reload_config",
            enabled=True,
            priority=100,
            source="builtin",
            examples=["/reload"]
        ),

        SlashCommandMetadata(
            name="stats",
            type=SlashCommandType.SYSTEM,
            description="Show orchestrator statistics",
            handler="_get_stats",
            enabled=True,
            priority=100,
            source="builtin",
            examples=["/stats"]
        ),

        SlashCommandMetadata(
            name="clear-cache",
            type=SlashCommandType.SYSTEM,
            description="Clear registry cache (force re-scan on next load)",
            handler="_clear_registry_cache",
            enabled=True,
            priority=100,
            source="builtin",
            examples=["/clear-cache"]
        ),

        # Meta-skill commands
        SlashCommandMetadata(
            name="master-orchestrator",
            type=SlashCommandType.SKILL,
            description="Master orchestrator meta-skill - analyzes user needs and intelligently routes to available resources",
            skill="master-orchestrator",
            enabled=True,
            priority=100,
            source="builtin",
            examples=[
                "/master-orchestrator 帮我审查代码质量",
                "/master-orchestrator 分析项目依赖关系",
                "/master-orchestrator 生成 API 文档"
            ]
        ),

        # Common shell commands
        SlashCommandMetadata(
            name="git-status",
            type=SlashCommandType.SHELL,
            description="Show git status",
            command="git status",
            enabled=True,
            priority=50,
            source="builtin",
            examples=["/git-status"]
        ),

        SlashCommandMetadata(
            name="git-log",
            type=SlashCommandType.SHELL,
            description="Show git log",
            command="git log --oneline -10",
            enabled=True,
            priority=50,
            source="builtin",
            examples=["/git-log", "/git-log -20"]
        ),

        SlashCommandMetadata(
            name="npm-test",
            type=SlashCommandType.SHELL,
            description="Run npm tests",
            command="npm test",
            enabled=True,
            priority=50,
            source="builtin",
            examples=["/npm-test"]
        ),
    ]

    # Register all builtin commands
    for cmd in builtin_commands:
        registry.register(cmd)

    logger.info(f"Registered {len(builtin_commands)} built-in slash commands")
