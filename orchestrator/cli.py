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
import getpass

from .constants import (
    MODE_KEYWORDS, ORCHESTRATED_MODES, MODE_MODEL_MAP, MODE_REASONING_MAP,
    SESSION_LIST_LIMIT, REASONING_NONE
)
from .utils import get_billing_provider, set_billing_provider, get_config

# Version
__version__ = "0.1.6"

# Colors
class C:
    ORANGE = "\033[38;5;208m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    DIM = "\033[2m"
    RESET = "\033[0m"

# ASCII Art Banner
BANNER = f"""{C.ORANGE}
     ██████╗ ███╗   ███╗██╗  ██╗
    ██╔═══██╗████╗ ████║╚██╗██╔╝
    ██║   ██║██╔████╔██║ ╚███╔╝
    ██║   ██║██║╚██╔╝██║ ██╔██╗
    ╚██████╔╝██║ ╚═╝ ██║██╔╝ ██╗
     ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝{C.RESET}
"""


def print_banner(model: str | None = None, provider: str | None = None) -> None:
    """Print the startup banner."""
    config = get_config()
    effective_model = model or config.get("model", {}).get("default", "gpt-5.3-codex")
    effective_provider = provider or get_billing_provider()
    user = getpass.getuser()
    cwd = Path.cwd()
    
    provider_label = "Codex Pro" if effective_provider == "codex" else "OpenAI API"
    
    print(BANNER)
    print(f"    {C.DIM}Oh My Codex{C.RESET} v{__version__}")
    print(f"    {C.CYAN}{effective_model}{C.RESET} · {C.GREEN}{provider_label}{C.RESET}")
    print(f"    {C.DIM}/{user}{C.RESET}")
    print()


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
    print_banner()
    
    config = get_config()
    
    # Reasoning
    reasoning = config.get("model", {}).get("reasoning", {}).get("default", "none")
    print(f"    🧠 Reasoning: {reasoning}")
    
    # Codex CLI
    try:
        result = subprocess.run(["codex", "--version"], capture_output=True, text=True)
        print(f"    ✅ Codex CLI: {result.stdout.strip()}")
    except FileNotFoundError:
        print("    ❌ Codex CLI: Not installed")
    
    # Agents SDK
    try:
        import agents
        print(f"    ✅ Agents SDK: Available")
    except ImportError:
        print("    ⚠️ Agents SDK: pip install oh-my-codex[full]")
    
    # Skills
    skills_dir = Path.home() / ".codex" / "skills"
    if skills_dir.exists():
        skills = [s for s in skills_dir.iterdir() if s.is_dir()]
        print(f"    📦 Skills: {len(skills)} installed")
    else:
        print("    ⚠️ Skills: None installed")
    
    # Config
    config_path = Path.home() / ".codex" / "config.yaml"
    print(f"    {'✅' if config_path.exists() else '⚠️'} Config: {config_path}")
    print()


def dispatch_prompt(prompt: str, mode_override: str | None = None,
                    model: str | None = None, provider: str | None = None,
                    reasoning: str | None = None, verbose: bool = False,
                    direct: bool = False) -> None:
    """Dispatch a prompt to the appropriate handler."""
    detected_mode, clean_prompt = detect_mode(prompt)
    mode = mode_override or detected_mode

    if direct or mode is None:
        effective_model = model or MODE_MODEL_MAP.get(mode)
        effective_reasoning = reasoning or MODE_REASONING_MAP.get(mode, REASONING_NONE)
        run_codex_direct(prompt, model=effective_model, provider=provider, reasoning=effective_reasoning)
    elif mode in ORCHESTRATED_MODES:
        run_orchestrator(clean_prompt, mode, verbose)
    else:
        effective_model = model or MODE_MODEL_MAP.get(mode)
        effective_reasoning = reasoning or MODE_REASONING_MAP.get(mode, REASONING_NONE)
        run_codex_direct(clean_prompt, model=effective_model, provider=provider, reasoning=effective_reasoning)


def interactive_mode() -> None:
    """Run omx in interactive REPL mode."""
    print_banner()
    print(f"    {C.DIM}Type a task to execute. Commands: status, list, help, clear, exit{C.RESET}")
    print()

    HELP_TEXT = f"""
  {C.CYAN}Usage:{C.RESET}
    Just type your task and press Enter.

  {C.CYAN}Mode keywords:{C.RESET}
    {C.ORANGE}autopilot:{C.RESET}  Full autonomous execution
    {C.ORANGE}ulw:{C.RESET}        Parallel multi-agent (ultrawork)
    {C.ORANGE}ralph:{C.RESET}      Persistent - never gives up
    {C.ORANGE}plan:{C.RESET}       Planning only, no execution
    {C.ORANGE}eco:{C.RESET}        Token-efficient, fast
    {C.ORANGE}tdd:{C.RESET}        Test-driven development
    {C.ORANGE}review:{C.RESET}     Code review
    {C.ORANGE}debug:{C.RESET}      Systematic debugging

  {C.CYAN}Commands:{C.RESET}
    {C.GREEN}status{C.RESET}   Show current config & status
    {C.GREEN}list{C.RESET}     List previous sessions
    {C.GREEN}help{C.RESET}     Show this help
    {C.GREEN}clear{C.RESET}    Clear screen
    {C.GREEN}exit{C.RESET}     Quit omx
"""

    while True:
        try:
            prompt = input(f"  {C.ORANGE}omx>{C.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n  {C.DIM}Bye!{C.RESET}")
            break

        if not prompt:
            continue

        cmd = prompt.lower()

        if cmd in ("exit", "quit", "q"):
            print(f"  {C.DIM}Bye!{C.RESET}")
            break
        elif cmd == "status":
            show_status()
        elif cmd == "list":
            list_sessions()
        elif cmd == "help":
            print(HELP_TEXT)
        elif cmd == "clear":
            os.system("clear" if os.name == "posix" else "cls")
            print_banner()
        else:
            try:
                dispatch_prompt(prompt)
            except SystemExit:
                pass  # Don't exit REPL on command failure
        print()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Oh My Codex - Multi-agent orchestration for Codex CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  omx                                    # Interactive mode
  omx "fix the bug"                      # Direct Codex
  omx "autopilot: build REST API"        # Full orchestration
  omx "ulw: refactor utils"              # Parallel execution
  omx "plan: design system"              # Planning mode
  omx "eco: quick fix"                   # Token-efficient

Keywords: autopilot, ulw (ultrawork), plan, eco, ralph
""",
    )

    parser.add_argument("-V", "--version", action="version", version=f"omx {__version__}")
    parser.add_argument("prompt", nargs="*", help="Task prompt")
    parser.add_argument("-m", "--mode", choices=["autopilot", "ultrawork", "plan", "eco"])
    parser.add_argument("--model", help="Model override")
    parser.add_argument("--provider", choices=["codex", "openai"], help="Billing provider override")
    parser.add_argument("--reasoning", choices=["none", "low", "medium", "high", "xhigh"],
                       help="Reasoning effort (xhigh for GPT-5.3-codex)")
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

    # No arguments → interactive mode
    if not args.prompt and not args.resume:
        interactive_mode()
        return

    prompt = " ".join(args.prompt) if args.prompt else ""

    if args.resume:
        detected_mode, clean_prompt = detect_mode(prompt)
        mode = args.mode or detected_mode
        run_orchestrator(clean_prompt, mode or "autopilot", args.verbose, args.resume)
        return

    dispatch_prompt(prompt, mode_override=args.mode, model=args.model,
                    provider=args.provider, reasoning=args.reasoning,
                    verbose=args.verbose, direct=args.direct)


if __name__ == "__main__":
    main()
