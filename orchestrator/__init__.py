"""
Oh My Codex Orchestrator
Multi-agent orchestration using Codex MCP + OpenAI Agents SDK.
"""

from .main import Orchestrator, run_orchestration
from .session import SessionManager, Session, SessionStatus
from .mcp import MCPManager, MCP_SERVERS
from .agents import AgentRole, AgentConfig, ModelTier, AGENT_CONFIGS
from .constants import MODE_KEYWORDS, ORCHESTRATED_MODES, MODE_MODEL_MAP
from .state import StateManager, ModeState, AgentActivity, TokenUsage, StateSnapshot
from .verify import Verifier, VerificationTier, VerificationResult, ProjectDetector
from .hud import HUD, HUDPreset, HUDRenderer, HUDData
from .analytics import AnalyticsEngine, AnalyticsSummary, AgentPerformanceMetrics
from .hooks import HookManager, HookEvent, HookConfig, HookResult, HookContext
from .notifications import NotificationManager, NotificationChannel, NotificationLevel, NotificationConfig, Notification, NotificationResult
from .skills import SkillManager, Skill, SkillMatch
from .context import ContextManager, MemoryEntry, MemoryScope, MemoryPriority
from .updater import Updater, VersionInfo
from .providers import ProviderManager, ProviderConfig, ProviderType, ProviderResponse, PROVIDER_MODELS, TASK_ROUTING
from .team import TeamBridge, Worker, TeamTask, WorkerStatus, TaskStatus

__version__ = "0.3.0"

__all__ = [
    "Orchestrator",
    "run_orchestration",
    "SessionManager",
    "Session",
    "SessionStatus",
    "MCPManager",
    "MCP_SERVERS",
    "AgentRole",
    "AgentConfig",
    "ModelTier",
    "AGENT_CONFIGS",
    "MODE_KEYWORDS",
    "ORCHESTRATED_MODES",
    "MODE_MODEL_MAP",
    # State management
    "StateManager",
    "ModeState",
    "AgentActivity",
    "TokenUsage",
    "StateSnapshot",
    # Verification
    "Verifier",
    "VerificationTier",
    "VerificationResult",
    "ProjectDetector",
    # HUD
    "HUD",
    "HUDPreset",
    "HUDRenderer",
    "HUDData",
    # Analytics
    "AnalyticsEngine",
    "AnalyticsSummary",
    "AgentPerformanceMetrics",
    # Hooks
    "HookManager",
    "HookEvent",
    "HookConfig",
    "HookResult",
    "HookContext",
    # Notifications
    "NotificationManager",
    "NotificationChannel",
    "NotificationLevel",
    "NotificationConfig",
    "Notification",
    "NotificationResult",
    # Skills
    "SkillManager",
    "Skill",
    "SkillMatch",
    # Context
    "ContextManager",
    "MemoryEntry",
    "MemoryScope",
    "MemoryPriority",
    # Updater
    "Updater",
    "VersionInfo",
    # Providers
    "ProviderManager",
    "ProviderConfig",
    "ProviderType",
    "ProviderResponse",
    "PROVIDER_MODELS",
    "TASK_ROUTING",
    # Team
    "TeamBridge",
    "Worker",
    "TeamTask",
    "WorkerStatus",
    "TaskStatus",
]
