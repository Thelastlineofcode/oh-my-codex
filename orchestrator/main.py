"""
Oh My Codex - Multi-Agent Orchestrator
Main entry point for orchestration.
"""

import asyncio
import os
import sys
from typing import Optional, List
from datetime import datetime

from .agents import AgentRole, AgentConfig, ModelTier, AGENT_CONFIGS, get_agent_config
from .session import SessionManager, Session, TaskRecord, SessionStatus
from .mcp import MCPManager

# Check for Agents SDK
try:
    from agents import Agent, Runner
    from agents.mcp import MCPServerStdio
    AGENTS_SDK_AVAILABLE = True
except ImportError:
    AGENTS_SDK_AVAILABLE = False


class Orchestrator:
    """
    Multi-agent orchestrator using Codex MCP + OpenAI Agents SDK.
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.session_manager = SessionManager()
        self.mcp_manager = MCPManager()
        self._agents = {}
        self._codex_mcp = None
    
    def log(self, msg: str, level: str = "info"):
        """Log a message if verbose mode is on."""
        if self.verbose:
            prefix = {"info": "ℹ️", "success": "✅", "error": "❌", "warn": "⚠️"}.get(level, "")
            print(f"{prefix} {msg}")
    
    async def _create_agent(self, role: AgentRole, mcp_servers: List = None) -> "Agent":
        """Create an agent with the specified role."""
        if not AGENTS_SDK_AVAILABLE:
            raise ImportError("openai-agents-sdk not installed")
        
        config = get_agent_config(role)
        if not config:
            raise ValueError(f"Unknown agent role: {role}")
        
        # Get handoff agents
        handoffs = []
        for handoff_role in config.handoff_to:
            if handoff_role not in self._agents:
                self._agents[handoff_role] = await self._create_agent(
                    handoff_role, mcp_servers
                )
            handoffs.append(self._agents[handoff_role])
        
        agent = Agent(
            name=config.name,
            instructions=config.instructions,
            model=config.model,
            mcp_servers=mcp_servers or [],
            handoffs=handoffs if handoffs else None,
        )
        
        return agent
    
    async def run(
        self,
        task: str,
        mode: str = "autopilot",
        agents: List[str] = None,
        session_id: str = None,
    ) -> dict:
        """
        Run an orchestrated task.
        
        Args:
            task: The task description
            mode: Execution mode (autopilot, ultrawork, plan, eco)
            agents: List of agent roles to use (default: based on mode)
            session_id: Resume an existing session
            
        Returns:
            dict with result and session info
        """
        if not AGENTS_SDK_AVAILABLE:
            return {
                "success": False,
                "error": "openai-agents-sdk not installed. Run: pip install openai-agents-sdk",
            }
        
        # Create or resume session
        if session_id:
            session = self.session_manager.resume(session_id)
            if not session:
                return {"success": False, "error": f"Session not found: {session_id}"}
            self.log(f"Resumed session: {session_id}", "info")
        else:
            session = self.session_manager.create(task, mode)
            self.log(f"Created session: {session.id}", "info")
        
        try:
            # Start Codex MCP server
            async with MCPServerStdio(
                name="Codex CLI",
                params=self.mcp_manager.get_codex_mcp_params()
            ) as codex_mcp:
                self._codex_mcp = codex_mcp
                
                # Determine which agents to use based on mode
                if agents:
                    agent_roles = [AgentRole(a) for a in agents]
                else:
                    agent_roles = self._get_agents_for_mode(mode)
                
                self.log(f"Mode: {mode}", "info")
                self.log(f"Agents: {', '.join(r.value for r in agent_roles)}", "info")
                
                # Create PM agent (always the entry point)
                pm = await self._create_agent(AgentRole.PM, [codex_mcp])
                
                # Prepare the prompt based on mode
                prompt = self._prepare_prompt(task, mode, session)
                
                self.log(f"Starting orchestration...", "info")
                self.log(f"Task: {task[:100]}{'...' if len(task) > 100 else ''}", "info")
                
                # Run the orchestration
                result = await Runner.run(pm, prompt)
                
                # Mark session complete
                self.session_manager.complete(session, success=True)
                
                return {
                    "success": True,
                    "result": result,
                    "session_id": session.id,
                    "mode": mode,
                }
                
        except Exception as e:
            self.session_manager.complete(session, success=False)
            return {
                "success": False,
                "error": str(e),
                "session_id": session.id,
            }
    
    def _get_agents_for_mode(self, mode: str) -> List[AgentRole]:
        """Determine which agents to use based on execution mode."""
        if mode == "eco":
            return [AgentRole.PM]  # Minimal, PM handles directly
        elif mode == "plan":
            return [AgentRole.PM, AgentRole.ARCHITECT]
        elif mode == "ultrawork":
            return [AgentRole.PM, AgentRole.FRONTEND, AgentRole.BACKEND, AgentRole.TESTER]
        else:  # autopilot (default)
            return [
                AgentRole.PM,
                AgentRole.FRONTEND,
                AgentRole.BACKEND,
                AgentRole.TESTER,
                AgentRole.REVIEWER,
            ]
    
    def _prepare_prompt(self, task: str, mode: str, session: Session) -> str:
        """Prepare the prompt based on mode and session context."""
        mode_instructions = {
            "autopilot": """AUTOPILOT MODE - Full autonomous execution.
1. Create a detailed plan
2. Execute each step
3. Verify results
4. Iterate until complete
Do not ask for confirmation - execute autonomously.""",
            
            "ultrawork": """ULTRAWORK MODE - Parallel execution.
1. Decompose into independent subtasks
2. Delegate to specialists in parallel
3. Aggregate and verify results
Focus on parallelization and speed.""",
            
            "plan": """PLAN MODE - Interview and planning only.
1. Ask clarifying questions (max 3)
2. Create detailed plan document
3. Get user approval before any execution
Do NOT execute - planning only.""",
            
            "eco": """ECO MODE - Minimal tokens, direct action.
- Skip explanations
- Execute directly
- Brief confirmation only
Optimize for speed and token efficiency.""",
        }
        
        instruction = mode_instructions.get(mode, mode_instructions["autopilot"])
        
        # Include session context if resuming
        context = ""
        if session.tasks:
            completed = [t for t in session.tasks if t.status == "completed"]
            if completed:
                context = f"\n\nPREVIOUS PROGRESS:\n"
                for t in completed:
                    context += f"- {t.description}: {t.result or 'Done'}\n"
        
        return f"""{instruction}

TASK: {task}
{context}
Begin now."""
    
    def list_sessions(self, status: str = None) -> List[dict]:
        """List all sessions."""
        status_enum = SessionStatus(status) if status else None
        sessions = self.session_manager.list_sessions(status_enum)
        return [s.to_dict() for s in sessions]
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get a specific session."""
        session = self.session_manager.load(session_id)
        return session.to_dict() if session else None


async def run_orchestration(
    task: str,
    mode: str = "autopilot",
    verbose: bool = True,
    session_id: str = None,
) -> dict:
    """
    Convenience function to run an orchestration.
    """
    orchestrator = Orchestrator(verbose=verbose)
    return await orchestrator.run(task, mode=mode, session_id=session_id)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Oh My Codex Orchestrator")
    parser.add_argument("task", nargs="?", help="Task to execute")
    parser.add_argument("-m", "--mode", default="autopilot",
                       choices=["autopilot", "ultrawork", "plan", "eco"],
                       help="Execution mode")
    parser.add_argument("-r", "--resume", help="Resume session ID")
    parser.add_argument("-l", "--list", action="store_true", help="List sessions")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.list:
        orchestrator = Orchestrator()
        sessions = orchestrator.list_sessions()
        if not sessions:
            print("No sessions found.")
        else:
            print(f"{'ID':<30} {'Status':<12} {'Mode':<12} {'Task':<40}")
            print("-" * 94)
            for s in sessions[:10]:
                task_preview = s["task"][:37] + "..." if len(s["task"]) > 40 else s["task"]
                print(f"{s['id']:<30} {s['status']:<12} {s['mode']:<12} {task_preview:<40}")
        return
    
    if not args.task and not args.resume:
        parser.print_help()
        sys.exit(1)
    
    task = args.task or ""
    result = asyncio.run(run_orchestration(
        task,
        mode=args.mode,
        verbose=args.verbose,
        session_id=args.resume,
    ))
    
    if result["success"]:
        print("\n✅ Orchestration complete!")
        print(f"Session: {result.get('session_id')}")
        if args.verbose:
            print(f"Result: {result.get('result')}")
    else:
        print(f"\n❌ Error: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
