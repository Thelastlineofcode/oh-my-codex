"""
Oh My Codex Orchestrator
Multi-agent orchestration using Codex MCP + OpenAI Agents SDK.
"""

from .main import Orchestrator, run_orchestration
from .session import SessionManager, Session, SessionStatus
from .mcp import MCPManager, MCP_SERVERS
from .agents import AgentRole, AgentConfig, ModelTier, AGENT_CONFIGS

__version__ = "0.1.0"

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
]
