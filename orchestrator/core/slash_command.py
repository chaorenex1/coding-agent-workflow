"""
Slash Command system for MasterOrchestrator V3.

Provides a unified command interface for all orchestrator operations:
- System commands: /discover, /list-skills, /reload
- Shell commands: /git-status, /npm-test
- Skill commands: /review-code, /commit
- Agent commands: /explore, /plan
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SlashCommandType(Enum):
    """Type of slash command."""
    SYSTEM = "system"      # System operations (/discover, /list-skills, /reload)
    SHELL = "shell"        # Shell command wrappers (/git-status, /npm-test)
    SKILL = "skill"        # Skill invocations (/review-code, /generate-doc)
    AGENT = "agent"        # Agent calls (/explore, /plan)
    PROMPT = "prompt"      # Prompt templates (/template-api-doc)


@dataclass
class SlashCommandMetadata:
    """Metadata for a slash command."""
    name: str                                    # Command name (without /)
    type: SlashCommandType                       # Command type
    description: str                             # Human-readable description

    # Type-specific configuration
    handler: Optional[str] = None                # Handler function name (for SYSTEM)
    command: Optional[str] = None                # Shell command (for SHELL)
    skill: Optional[str] = None                  # Skill name (for SKILL)
    agent_type: Optional[str] = None             # Agent type (for AGENT)
    prompt_template: Optional[str] = None        # Prompt template name (for PROMPT)

    # Metadata
    enabled: bool = True
    priority: int = 50                           # 0-1000, higher = higher priority
    source: str = "builtin"                      # "builtin", "user", or "project"
    dependencies: List[str] = field(default_factory=list)  # Dependencies

    # Arguments
    args_schema: Optional[Dict[str, Any]] = None  # Expected arguments
    examples: List[str] = field(default_factory=list)  # Usage examples

    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)  # Additional config

    @property
    def full_name(self) -> str:
        """Get full command name with slash."""
        return f"/{self.name}"

    def __repr__(self) -> str:
        return f"SlashCommand(/{self.name}, type={self.type.value})"


@dataclass
class SlashCommandResult:
    """Result of executing a slash command."""
    command: str                                 # Command that was executed
    success: bool                                # Whether execution succeeded
    output: Any = None                           # Command output
    error: Optional[str] = None                  # Error message if failed
    executed_at: Optional[datetime] = None       # Execution timestamp
    duration_seconds: float = 0.0                # Execution duration
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata

    def __repr__(self) -> str:
        status = "✓" if self.success else "✗"
        return f"SlashCommandResult({status} {self.command}, {self.duration_seconds:.2f}s)"


class SlashCommandHandler:
    """Base class for slash command handlers."""

    def __init__(self, orchestrator=None):
        """
        Initialize handler.

        Args:
            orchestrator: MasterOrchestrator instance (for accessing resources)
        """
        self.orchestrator = orchestrator
        logger.debug(f"{self.__class__.__name__} initialized")

    def execute(self, command: SlashCommandMetadata, args: List[str],
                kwargs: Dict[str, Any]) -> SlashCommandResult:
        """
        Execute the command.

        Args:
            command: Command metadata
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            SlashCommandResult
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def validate_args(self, command: SlashCommandMetadata, args: List[str]) -> bool:
        """
        Validate command arguments.

        Args:
            command: Command metadata
            args: Arguments to validate

        Returns:
            True if valid, False otherwise
        """
        # Default: no validation
        return True


class SystemCommandHandler(SlashCommandHandler):
    """Handler for system commands (/discover, /list-skills, etc.)."""

    def execute(self, command: SlashCommandMetadata, args: List[str],
                kwargs: Dict[str, Any]) -> SlashCommandResult:
        """Execute system command."""
        start_time = datetime.now()

        try:
            # Get handler method from orchestrator
            handler_name = command.handler
            if not handler_name:
                raise ValueError(f"System command '{command.name}' has no handler specified")

            if not hasattr(self.orchestrator, handler_name):
                raise ValueError(f"Handler '{handler_name}' not found in orchestrator")

            handler_method = getattr(self.orchestrator, handler_name)

            # Execute handler
            output = handler_method(*args, **kwargs)

            duration = (datetime.now() - start_time).total_seconds()

            return SlashCommandResult(
                command=command.full_name,
                success=True,
                output=output,
                executed_at=start_time,
                duration_seconds=round(duration, 3)
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"System command '{command.name}' failed: {e}")

            return SlashCommandResult(
                command=command.full_name,
                success=False,
                error=str(e),
                executed_at=start_time,
                duration_seconds=round(duration, 3)
            )


class ShellCommandHandler(SlashCommandHandler):
    """Handler for shell commands (/git-status, /npm-test, etc.)."""

    def execute(self, command: SlashCommandMetadata, args: List[str],
                kwargs: Dict[str, Any]) -> SlashCommandResult:
        """Execute shell command."""
        start_time = datetime.now()

        try:
            # Get shell command
            shell_cmd = command.command
            if not shell_cmd:
                raise ValueError(f"Shell command '{command.name}' has no command specified")

            # Append args to command
            if args:
                shell_cmd = f"{shell_cmd} {' '.join(args)}"

            # Execute via CommandExecutor
            from orchestrator.executors.command_executor import CommandExecutor

            if not self.orchestrator or not hasattr(self.orchestrator, 'backend_orch'):
                raise ValueError("Orchestrator not properly initialized")

            executor = CommandExecutor(self.orchestrator.backend_orch)
            result = executor.execute(shell_cmd, **kwargs)

            duration = (datetime.now() - start_time).total_seconds()

            return SlashCommandResult(
                command=command.full_name,
                success=result.success,
                output=result.output,
                error=result.error if not result.success else None,
                executed_at=start_time,
                duration_seconds=round(duration, 3)
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Shell command '{command.name}' failed: {e}")

            return SlashCommandResult(
                command=command.full_name,
                success=False,
                error=str(e),
                executed_at=start_time,
                duration_seconds=round(duration, 3)
            )


class SkillCommandHandler(SlashCommandHandler):
    """Handler for skill commands (/review-code, /commit, etc.)."""

    def execute(self, command: SlashCommandMetadata, args: List[str],
                kwargs: Dict[str, Any]) -> SlashCommandResult:
        """Execute skill command."""
        start_time = datetime.now()

        try:
            # Get skill name
            skill_name = command.skill
            if not skill_name:
                raise ValueError(f"Skill command '{command.name}' has no skill specified")

            # Build request from args
            request = ' '.join(args) if args else kwargs.get('request', '')

            # Execute via SkillExecutor or direct skill call
            if self.orchestrator and hasattr(self.orchestrator, 'factory'):
                executor = self.orchestrator.factory.create_executor(f"skill:{skill_name}")
                if not executor:
                    raise ValueError(f"Skill '{skill_name}' not found")

                output = executor.execute(request)
            else:
                raise ValueError("Orchestrator factory not available")

            duration = (datetime.now() - start_time).total_seconds()

            return SlashCommandResult(
                command=command.full_name,
                success=True,
                output=output,
                executed_at=start_time,
                duration_seconds=round(duration, 3)
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Skill command '{command.name}' failed: {e}")

            return SlashCommandResult(
                command=command.full_name,
                success=False,
                error=str(e),
                executed_at=start_time,
                duration_seconds=round(duration, 3)
            )


class AgentCommandHandler(SlashCommandHandler):
    """Handler for agent commands (/explore, /plan, etc.)."""

    def execute(self, command: SlashCommandMetadata, args: List[str],
                kwargs: Dict[str, Any]) -> SlashCommandResult:
        """Execute agent command."""
        start_time = datetime.now()

        try:
            # Get agent type
            agent_type = command.agent_type
            if not agent_type:
                raise ValueError(f"Agent command '{command.name}' has no agent_type specified")

            # Build request from args
            request = ' '.join(args) if args else kwargs.get('request', '')

            # Execute via AgentCaller
            from orchestrator.executors.agent_caller import AgentCaller

            if not self.orchestrator or not hasattr(self.orchestrator, 'backend_orch'):
                raise ValueError("Orchestrator not properly initialized")

            caller = AgentCaller(self.orchestrator.backend_orch)
            result = caller.call_agent(request, agent_type=agent_type, **kwargs)

            duration = (datetime.now() - start_time).total_seconds()

            return SlashCommandResult(
                command=command.full_name,
                success=result.success,
                output=result.output,
                error=result.error if not result.success else None,
                executed_at=start_time,
                duration_seconds=round(duration, 3)
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Agent command '{command.name}' failed: {e}")

            return SlashCommandResult(
                command=command.full_name,
                success=False,
                error=str(e),
                executed_at=start_time,
                duration_seconds=round(duration, 3)
            )


# Handler mapping
HANDLER_MAP = {
    SlashCommandType.SYSTEM: SystemCommandHandler,
    SlashCommandType.SHELL: ShellCommandHandler,
    SlashCommandType.SKILL: SkillCommandHandler,
    SlashCommandType.AGENT: AgentCommandHandler,
    # SlashCommandType.PROMPT: PromptCommandHandler,  # TODO: implement
}


def get_handler(command_type: SlashCommandType, orchestrator=None) -> SlashCommandHandler:
    """
    Get appropriate handler for command type.

    Args:
        command_type: Type of command
        orchestrator: MasterOrchestrator instance

    Returns:
        SlashCommandHandler instance
    """
    handler_class = HANDLER_MAP.get(command_type)
    if not handler_class:
        raise ValueError(f"No handler registered for command type: {command_type}")

    return handler_class(orchestrator=orchestrator)
