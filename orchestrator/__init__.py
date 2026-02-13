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

__version__ = "0.1.6"

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
]
