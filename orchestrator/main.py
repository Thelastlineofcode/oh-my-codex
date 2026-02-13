"""
Oh My Codex - Multi-Agent Orchestrator
Main entry point for orchestration.
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
from typing import Any, TYPE_CHECKING
from datetime import datetime

from .agents import AgentRole, AgentConfig, ModelTier, AGENT_CONFIGS, get_agent_config
from .constants import MODE_REASONING_MAP, REASONING_NONE, VERIFY_SKIP_MODES
from .tools import ALL_TOOLS, get_tools_for_role
from .state import StateManager
from .verify import Verifier, VerificationTier

if TYPE_CHECKING:
    from agents import Agent

logger = logging.getLogger(__name__)
from .session import SessionManager, Session, TaskRecord, SessionStatus
from .mcp import MCPManager

# Check for Agents SDK (pip install openai-agents)
try:
    from agents import Agent, Runner, function_tool
    AGENTS_SDK_AVAILABLE = True
except ImportError:
    AGENTS_SDK_AVAILABLE = False


class Orchestrator:
    """
    Multi-agent orchestrator using OpenAI Agents SDK.
    Supports parallel execution, handoffs, and tool use.
    """
    
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self.session_manager = SessionManager()
        self.mcp_manager = MCPManager()
        self.state_manager = StateManager()
        self._agents: dict[str, Agent] = {}
    
    def log(self, msg: str, level: str = "info") -> None:
        """Log a message if verbose mode is on."""
        log_func = getattr(logger, level if level != "success" else "info", logger.info)
        log_func(msg)
        
        if self.verbose:
            prefix = {"info": "ℹ️", "success": "✅", "error": "❌", "warn": "⚠️"}.get(level, "")
            print(f"{prefix} {msg}")
    
    def _get_cache_key(self, role: AgentRole) -> str:
        """Generate cache key for agent."""
        return f"{role.value}"
    
    def _create_agent_sync(self, role: AgentRole, handoff_roles: list[AgentRole] | None = None) -> Agent:
        """Create an agent with the specified role (sync version for setup)."""
        if not AGENTS_SDK_AVAILABLE:
            raise ImportError("openai-agents not installed. Run: pip install openai-agents")
        
        cache_key = self._get_cache_key(role)
        if cache_key in self._agents:
            return self._agents[cache_key]
        
        config = get_agent_config(role)
        if not config:
            raise ValueError(f"Unknown agent role: {role}")
        
        # Get tools for this role
        tools = get_tools_for_role(role.value)
        
        # Build handoffs (but don't recurse infinitely)
        handoffs = []
        if handoff_roles:
            for handoff_role in handoff_roles:
                if handoff_role != role:  # Avoid self-reference
                    handoff_agent = self._create_agent_sync(handoff_role, None)
                    handoffs.append(handoff_agent)
        
        agent = Agent(
            name=config.name,
            instructions=config.instructions,
            model=config.model,
            tools=tools,
            handoffs=handoffs if handoffs else None,
        )
        
        self._agents[cache_key] = agent
        return agent
    
    async def run(
        self,
        task: str,
        mode: str = "autopilot",
        agents: list[str] | None = None,
        session_id: str | None = None,
        reasoning: str | None = None,
    ) -> dict[str, Any]:
        """
        Run an orchestrated task.
        
        Args:
            task: The task description
            mode: Execution mode (autopilot, ultrawork, plan, eco, etc.)
            agents: List of agent roles to use (default: based on mode)
            session_id: Resume an existing session
            reasoning: Reasoning effort level
            
        Returns:
            dict with result and session info
        """
        if not AGENTS_SDK_AVAILABLE:
            return {
                "success": False,
                "error": "openai-agents not installed. Run: pip install openai-agents",
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
            # Start state tracking
            self.state_manager.start_mode(mode, session.id)

            # Determine which agents to use based on mode
            agent_roles = self._get_agents_for_mode(mode)

            self.log(f"Mode: {mode}", "info")
            self.log(f"Agents: {', '.join(r.value for r in agent_roles)}", "info")
            
            # Get reasoning effort
            effective_reasoning = reasoning or MODE_REASONING_MAP.get(mode, REASONING_NONE)
            if effective_reasoning != REASONING_NONE:
                self.log(f"Reasoning: {effective_reasoning}", "info")
            
            # Create PM agent with handoffs to other agents
            handoff_roles = agent_roles[1:] if len(agent_roles) > 1 else None
            pm = self._create_agent_sync(AgentRole.PM, handoff_roles)
            
            # Prepare the prompt based on mode
            prompt = self._prepare_prompt(task, mode, session, effective_reasoning)
            
            self.log(f"Starting orchestration...", "info")
            self.log(f"Task: {task[:100]}{'...' if len(task) > 100 else ''}", "info")
            self.state_manager.update_phase(session.id, "executing")

            # Choose execution strategy
            if mode == "ultrawork" and len(agent_roles) > 2:
                result = await self._run_parallel(task, agent_roles, prompt)
            else:
                result = await Runner.run(pm, prompt)

            # Extract final output
            final_output = getattr(result, 'final_output', str(result))

            # Log agent activities
            for role in agent_roles:
                self.state_manager.log_agent(session.id, role.value, "completed")

            # Verification step (skip for certain modes)
            if mode not in VERIFY_SKIP_MODES:
                self.state_manager.update_phase(session.id, "verifying")
                self.log("Running verification...", "info")
                verifier = Verifier()
                vresult = verifier.verify(mode=mode)
                if not vresult.passed:
                    self.log(f"Verification: {vresult.summary}", "warn")
                else:
                    self.log(f"Verification passed: {vresult.summary}", "success")

            # Mark session complete
            self.state_manager.update_phase(session.id, "completed")
            self.state_manager.end_mode(session.id)
            self.session_manager.complete(session, success=True)

            return {
                "success": True,
                "result": final_output,
                "session_id": session.id,
                "mode": mode,
                "agents_used": [r.value for r in agent_roles],
            }

        except Exception as e:
            self.log(f"Error: {str(e)}", "error")
            self.state_manager.end_mode(session.id)
            self.session_manager.complete(session, success=False)
            return {
                "success": False,
                "error": str(e),
                "session_id": session.id,
            }
    
    async def _run_parallel(
        self,
        task: str,
        agent_roles: list[AgentRole],
        base_prompt: str,
    ) -> Any:
        """
        Run multiple agents in parallel for ultrawork mode.
        """
        self.log("Starting parallel execution...", "info")
        
        # Create coordinator to manage results
        coordinator = self._create_agent_sync(AgentRole.COORDINATOR)
        
        # Decompose task into subtasks using coordinator
        decompose_prompt = f"""Analyze this task and break it into independent subtasks for parallel execution:

TASK: {task}

Output a numbered list of subtasks that can be executed independently.
Keep subtasks focused and actionable."""
        
        decomposition = await Runner.run(coordinator, decompose_prompt)
        subtasks = getattr(decomposition, 'final_output', str(decomposition))
        
        self.log(f"Decomposed into subtasks", "info")
        
        # Create parallel tasks for each specialist agent
        specialist_roles = [r for r in agent_roles if r not in [AgentRole.PM, AgentRole.COORDINATOR]]
        
        async def run_agent(role: AgentRole, subtask_context: str) -> tuple[str, str]:
            """Run a single agent on a subtask."""
            agent = self._create_agent_sync(role)
            prompt = f"""You are working on part of a larger task.

OVERALL TASK: {task}

YOUR ASSIGNMENT:
{subtask_context}

Execute your part and report results."""
            
            try:
                result = await Runner.run(agent, prompt)
                output = getattr(result, 'final_output', str(result))
                return (role.value, output)
            except Exception as e:
                return (role.value, f"[ERROR] {str(e)}")
        
        # Run agents in parallel
        if specialist_roles:
            tasks = [
                run_agent(role, f"Handle the {role.value} aspects of this task.\n\nSubtasks:\n{subtasks}")
                for role in specialist_roles
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Aggregate results
            aggregated = []
            for item in results:
                if isinstance(item, tuple):
                    role, output = item
                    aggregated.append(f"## {role.upper()}\n{output}")
                else:
                    aggregated.append(f"[ERROR] {str(item)}")
            
            # Final synthesis by PM
            pm = self._create_agent_sync(AgentRole.PM)
            synthesis_prompt = f"""You coordinated a parallel execution of this task:

TASK: {task}

RESULTS FROM AGENTS:
{chr(10).join(aggregated)}

Synthesize these results into a cohesive final output.
Resolve any conflicts and ensure completeness."""
            
            final_result = await Runner.run(pm, synthesis_prompt)
            return final_result
        
        # Fallback to single agent
        pm = self._create_agent_sync(AgentRole.PM)
        return await Runner.run(pm, base_prompt)
    
    def _get_agents_for_mode(self, mode: str) -> list[AgentRole]:
        """Determine which agents to use based on execution mode."""
        mode_agents = {
            "eco": [AgentRole.EXECUTOR],
            "plan": [AgentRole.PM, AgentRole.PLANNER, AgentRole.ARCHITECT],
            "ralplan": [AgentRole.PM, AgentRole.PLANNER, AgentRole.CRITIC],
            "ultrawork": [AgentRole.PM, AgentRole.COORDINATOR, AgentRole.FRONTEND, AgentRole.BACKEND, AgentRole.TESTER],
            "ultrapilot": [AgentRole.PM, AgentRole.COORDINATOR, AgentRole.FRONTEND, AgentRole.BACKEND, AgentRole.TESTER, AgentRole.REVIEWER],
            "team": [AgentRole.PM, AgentRole.PLANNER, AgentRole.EXECUTOR, AgentRole.TESTER, AgentRole.REVIEWER],
            "ralph": [AgentRole.PM, AgentRole.EXECUTOR, AgentRole.TESTER, AgentRole.DEBUGGER],
            "pipeline": [AgentRole.PM, AgentRole.PLANNER, AgentRole.EXECUTOR],
            "tdd": [AgentRole.PM, AgentRole.TESTER, AgentRole.EXECUTOR],
            "review": [AgentRole.PM, AgentRole.REVIEWER, AgentRole.SECURITY],
            "research": [AgentRole.PM, AgentRole.RESEARCHER, AgentRole.ANALYST],
            "deepsearch": [AgentRole.PM, AgentRole.EXPLORER, AgentRole.ANALYST],
            "debug": [AgentRole.PM, AgentRole.DEBUGGER, AgentRole.ANALYST],
        }
        
        # Default: autopilot
        return mode_agents.get(mode, [
            AgentRole.PM,
            AgentRole.EXECUTOR,
            AgentRole.TESTER,
            AgentRole.REVIEWER,
        ])
    
    def _prepare_prompt(self, task: str, mode: str, session: Session, reasoning: str) -> str:
        """Prepare the prompt based on mode and session context."""
        mode_instructions = {
            "autopilot": """AUTOPILOT MODE - Full autonomous execution.
1. Create a detailed plan
2. Execute each step using tools
3. Verify results
4. Iterate until complete
Do not ask for confirmation - execute autonomously.""",
            
            "ultrawork": """ULTRAWORK MODE - Parallel execution.
1. Decompose into independent subtasks
2. Delegate to specialists in parallel
3. Aggregate and verify results
Focus on parallelization and speed.""",
            
            "ultrapilot": """ULTRAPILOT MODE - Maximum parallel agents.
1. Analyze and decompose task
2. Spawn maximum parallel agents
3. Execute all tracks simultaneously
4. Merge and verify results
Maximum speed through parallelization.""",
            
            "team": """TEAM MODE - Staged pipeline orchestration.
Pipeline: plan → prd → exec → verify → fix (loop)
1. Create structured plan
2. Generate PRD with acceptance criteria
3. Execute with specialized agents
4. Verify against criteria
5. Fix any issues (loop until passing)
Coordinated team execution.""",
            
            "ralph": """RALPH MODE - Persistent execution (never give up).
1. Attempt the task
2. Verify completion
3. If not complete, fix and retry
4. Loop until FULLY verified complete
NEVER give up. NEVER declare partial success.
Use all available tools to achieve the goal.""",
            
            "pipeline": """PIPELINE MODE - Sequential staged processing.
1. Define pipeline stages
2. Execute each stage in order
3. Pass output to next stage
4. Verify final output
Strict sequential execution.""",
            
            "ralplan": """RALPLAN MODE - Iterative planning with consensus.
Round 1: Create initial plan
Round 2: Critique and challenge
Round 3: Refine based on feedback
Continue until consensus reached.""",
            
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
            
            "tdd": """TDD MODE - Test-Driven Development.
1. Write failing test first
2. Implement minimal code to pass
3. Refactor
4. Repeat
Red → Green → Refactor cycle.""",
            
            "review": """REVIEW MODE - Comprehensive code review.
Check: Security, Performance, Correctness, Maintainability
Output: Issues by severity with specific fixes
Verdict: Approve / Request Changes.""",
            
            "research": """RESEARCH MODE - Deep research and analysis.
1. Define research question
2. Gather sources
3. Analyze and compare
4. Synthesize findings
5. Provide recommendation.""",
            
            "deepsearch": """DEEPSEARCH MODE - Codebase exploration.
1. Map structure using list_directory and search_files
2. Find relevant files
3. Trace code paths
4. Document findings.""",
            
            "debug": """DEBUG MODE - Systematic debugging.
1. Reproduce the issue
2. Isolate the cause
3. Form hypothesis
4. Test and verify
5. Apply fix
6. Confirm resolution.""",
        }
        
        instruction = mode_instructions.get(mode, mode_instructions["autopilot"])
        
        # Add reasoning instruction
        reasoning_note = ""
        if reasoning and reasoning != REASONING_NONE:
            reasoning_note = f"\n\nREASONING LEVEL: {reasoning.upper()} - Think {'deeply' if reasoning in ['high', 'xhigh'] else 'carefully'} before acting."
        
        # Include session context if resuming
        context = ""
        if session.tasks:
            completed = [t for t in session.tasks if t.status == "completed"]
            if completed:
                context = f"\n\nPREVIOUS PROGRESS:\n"
                for t in completed:
                    context += f"- {t.description}: {t.result or 'Done'}\n"
        
        return f"""{instruction}
{reasoning_note}
TASK: {task}
{context}
You have access to tools: run_shell, read_file, write_file, edit_file, list_directory, search_files, git_status, git_diff, run_tests.

Begin now."""
    
    def list_sessions(self, status: str | None = None) -> list[dict[str, Any]]:
        """List all sessions."""
        status_enum = SessionStatus(status) if status else None
        sessions = self.session_manager.list_sessions(status_enum)
        return [s.to_dict() for s in sessions]
    
    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Get a specific session."""
        session = self.session_manager.load(session_id)
        return session.to_dict() if session else None


async def run_orchestration(
    task: str,
    mode: str = "autopilot",
    verbose: bool = True,
    session_id: str | None = None,
    reasoning: str | None = None,
) -> dict:
    """
    Convenience function to run an orchestration.
    """
    orchestrator = Orchestrator(verbose=verbose)
    return await orchestrator.run(task, mode=mode, session_id=session_id, reasoning=reasoning)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Oh My Codex Orchestrator")
    parser.add_argument("task", nargs="?", help="Task to execute")
    parser.add_argument("-m", "--mode", default="autopilot",
                       choices=["autopilot", "ultrawork", "ultrapilot", "team", 
                               "ralph", "pipeline", "plan", "eco", "tdd", 
                               "review", "research", "deepsearch", "debug"],
                       help="Execution mode")
    parser.add_argument("-r", "--resume", help="Resume session ID")
    parser.add_argument("-l", "--list", action="store_true", help="List sessions")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--reasoning", choices=["none", "low", "medium", "high", "xhigh"],
                       help="Reasoning effort level")
    
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
        reasoning=args.reasoning,
    ))
    
    if result["success"]:
        print("\n✅ Orchestration complete!")
        print(f"Session: {result.get('session_id')}")
        if result.get("agents_used"):
            print(f"Agents: {', '.join(result['agents_used'])}")
        if args.verbose and result.get("result"):
            print(f"\n--- Result ---\n{result['result']}")
    else:
        print(f"\n❌ Error: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
