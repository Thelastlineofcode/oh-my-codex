"""
CLI entry point for pip-installed oh-my-codex.
"""
from __future__ import annotations

import sys
import os

# Allow running from source without install
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
import argparse
import subprocess

from .constants import (
    MODE_KEYWORDS, ORCHESTRATED_MODES, MODE_MODEL_MAP, MODE_REASONING_MAP,
    SESSION_LIST_LIMIT, REASONING_NONE
)
from .utils import get_billing_provider, set_billing_provider, get_config


def detect_mode(prompt: str) -> tuple[str | None, str]:
    """Detect execution mode from prompt keywords."""
    prompt_lower = prompt.lower()
    for keyword, mode in MODE_KEYWORDS.items():
        if prompt_lower.startswith(keyword):
            clean_prompt = prompt[len(keyword):].strip()
            return mode, clean_prompt
    return None, prompt


def run_codex_direct(
    prompt: str,
    model: str | None = None,
    approval: str | None = None,
    provider: str | None = None,
    reasoning: str | None = None,
) -> None:
    """Run Codex CLI directly."""
    cmd = ["codex"]
    
    # Add provider from config or parameter
    effective_provider = provider or get_billing_provider()
    cmd.extend(["--provider", effective_provider])
    
    if model:
        cmd.extend(["--model", model])
    if approval:
        cmd.extend(["--approval-mode", approval])
    
    # Add reasoning effort if specified and not "none"
    if reasoning and reasoning != REASONING_NONE:
        cmd.extend(["-c", f'reasoning.effort="{reasoning}"'])
    
    cmd.append(prompt)
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("❌ Codex CLI not found. Install: npm install -g @openai/codex")
        sys.exit(127)  # Command not found
    except PermissionError:
        print("❌ Permission denied to run Codex CLI")
        sys.exit(126)  # Cannot execute
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


def run_orchestrator(prompt: str, mode: str, verbose: bool = False, resume: str | None = None) -> None:
    """Run the orchestrator."""
    try:
        import asyncio
        from .main import run_orchestration
        
        result = asyncio.run(run_orchestration(
            prompt,
            mode=mode,
            verbose=verbose,
            session_id=resume,
        ))
        
        if result["success"]:
            print(f"\n✅ Complete! Session: {result.get('session_id')}")
        else:
            print(f"\n❌ Error: {result.get('error')}")
            sys.exit(1)
            
    except ImportError as e:
        print(f"⚠️ Orchestrator unavailable: {e}")
        print("Falling back to direct Codex...")
        run_codex_direct(prompt)


def list_sessions() -> None:
    """List sessions."""
    try:
        from .session import SessionManager
        
        manager = SessionManager()
        sessions = manager.list_sessions()
        
        if not sessions:
            print("No sessions found.")
            return
        
        print(f"\n{'ID':<32} {'Status':<10} {'Mode':<10} {'Task'}")
        print("-" * 80)
        for s in sessions[:SESSION_LIST_LIMIT]:
            task_preview = s.task[:30] + "..." if len(s.task) > 30 else s.task
            print(f"{s.id:<32} {s.status.value:<10} {s.mode:<10} {task_preview}")
        
    except ImportError:
        print("❌ Session manager not available")
        sys.exit(1)


def show_status() -> None:
    """Show status."""
    print("🚀 Oh My Codex Status\n")
    
    # Billing provider
    provider = get_billing_provider()
    provider_display = "Codex Pro (subscription)" if provider == "codex" else "OpenAI API (pay-per-use)"
    print(f"💳 Billing: {provider_display}")
    
    # Default model
    config = get_config()
    model = config.get("model", {}).get("default", "gpt-5.1-codex")
    print(f"🤖 Default Model: {model}")
    
    # Default reasoning
    reasoning = config.get("model", {}).get("reasoning", {}).get("default", "none")
    print(f"🧠 Reasoning: {reasoning}")
    
    # Codex CLI
    try:
        result = subprocess.run(["codex", "--version"], capture_output=True, text=True)
        print(f"✅ Codex CLI: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Codex CLI: Not installed")
    
    # Agents SDK
    try:
        import agents
        print(f"✅ OpenAI Agents SDK: Available")
    except ImportError:
        print("⚠️ OpenAI Agents SDK: Not installed (pip install oh-my-codex[full])")
    
    # Skills
    skills_dir = Path.home() / ".codex" / "skills"
    if skills_dir.exists():
        skills = [s for s in skills_dir.iterdir() if s.is_dir()]
        print(f"✅ Skills: {len(skills)} installed")
        for skill in skills:
            print(f"   - {skill.name}")
    else:
        print("⚠️ Skills: None installed")
    
    # Config
    config_path = Path.home() / ".codex" / "config.toml"
    print(f"{'✅' if config_path.exists() else '⚠️'} Config: {config_path}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Oh My Codex - Multi-agent orchestration for Codex CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  omx "fix the bug"                      # Direct Codex
  omx "autopilot: build REST API"        # Full orchestration
  omx "ulw: refactor utils"              # Parallel execution
  omx "plan: design system"              # Planning mode
  omx "eco: quick fix"                   # Token-efficient

Keywords: autopilot, ulw (ultrawork), plan, eco, ralph
""",
    )
    
    parser.add_argument("prompt", nargs="*", help="Task prompt")
    parser.add_argument("-m", "--mode", choices=["autopilot", "ultrawork", "plan", "eco"])
    parser.add_argument("--model", help="Model override")
    parser.add_argument("--provider", choices=["codex", "openai"], help="Billing provider override")
    parser.add_argument("--reasoning", choices=["none", "low", "medium", "high"], 
                       help="Reasoning effort (for GPT-5.1+)")
    parser.add_argument("-r", "--resume", help="Resume session")
    parser.add_argument("-l", "--list", action="store_true", help="List sessions")
    parser.add_argument("-s", "--status", action="store_true", help="Show status")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--direct", action="store_true", help="Skip orchestration")
    parser.add_argument("--set-provider", choices=["codex", "openai"], help="Change default billing provider")
    
    args = parser.parse_args()
    
    if args.set_provider:
        set_billing_provider(args.set_provider)
        return
    
    if args.status:
        show_status()
        return
    
    if args.list:
        list_sessions()
        return
    
    if not args.prompt and not args.resume:
        parser.print_help()
        return
    
    prompt = " ".join(args.prompt) if args.prompt else ""
    detected_mode, clean_prompt = detect_mode(prompt)
    mode = args.mode or detected_mode
    
    if args.resume:
        run_orchestrator(clean_prompt, mode or "autopilot", args.verbose, args.resume)
        return
    
    if args.direct or mode is None:
        model = args.model or MODE_MODEL_MAP.get(mode)
        reasoning = args.reasoning or MODE_REASONING_MAP.get(mode, REASONING_NONE)
        run_codex_direct(prompt, model=model, provider=args.provider, reasoning=reasoning)
    elif mode in ORCHESTRATED_MODES:
        run_orchestrator(clean_prompt, mode, args.verbose)
    else:
        # Direct modes with model routing
        model = args.model or MODE_MODEL_MAP.get(mode)
        reasoning = args.reasoning or MODE_REASONING_MAP.get(mode, REASONING_NONE)
        run_codex_direct(clean_prompt, model=model, provider=args.provider, reasoning=reasoning)


if __name__ == "__main__":
    main()
