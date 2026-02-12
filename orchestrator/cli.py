"""
CLI entry point for pip-installed oh-my-codex.
"""

import sys
import os

# Allow running from source without install
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
import argparse
import subprocess

# Keywords that trigger special modes
MODE_KEYWORDS = {
    "autopilot:": "autopilot",
    "autopilot ": "autopilot",
    "ulw:": "ultrawork",
    "ulw ": "ultrawork",
    "ultrawork:": "ultrawork",
    "plan:": "plan",
    "plan ": "plan",
    "eco:": "eco",
    "eco ": "eco",
    "ralph:": "autopilot",
    "ralph ": "autopilot",
}


def detect_mode(prompt: str) -> tuple:
    """Detect execution mode from prompt keywords."""
    prompt_lower = prompt.lower()
    for keyword, mode in MODE_KEYWORDS.items():
        if prompt_lower.startswith(keyword):
            clean_prompt = prompt[len(keyword):].strip()
            return mode, clean_prompt
    return None, prompt


def run_codex_direct(prompt: str, model: str = None, approval: str = None):
    """Run Codex CLI directly."""
    cmd = ["codex"]
    if model:
        cmd.extend(["--model", model])
    if approval:
        cmd.extend(["--approval-mode", approval])
    cmd.append(prompt)
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("❌ Codex CLI not found. Install: npm install -g @openai/codex")
        sys.exit(1)


def run_orchestrator(prompt: str, mode: str, verbose: bool = False, resume: str = None):
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


def list_sessions():
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
        for s in sessions[:15]:
            task_preview = s.task[:30] + "..." if len(s.task) > 30 else s.task
            print(f"{s.id:<32} {s.status.value:<10} {s.mode:<10} {task_preview}")
        
    except ImportError:
        print("❌ Session manager not available")
        sys.exit(1)


def show_status():
    """Show status."""
    print("🚀 Oh My Codex Status\n")
    
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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Oh My Codex - Multi-agent orchestration for Codex CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  omc "fix the bug"                      # Direct Codex
  omc "autopilot: build REST API"        # Full orchestration
  omc "ulw: refactor utils"              # Parallel execution
  omc "plan: design system"              # Planning mode
  omc "eco: quick fix"                   # Token-efficient

Keywords: autopilot, ulw (ultrawork), plan, eco, ralph
""",
    )
    
    parser.add_argument("prompt", nargs="*", help="Task prompt")
    parser.add_argument("-m", "--mode", choices=["autopilot", "ultrawork", "plan", "eco"])
    parser.add_argument("--model", help="Model override")
    parser.add_argument("-r", "--resume", help="Resume session")
    parser.add_argument("-l", "--list", action="store_true", help="List sessions")
    parser.add_argument("-s", "--status", action="store_true", help="Show status")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--direct", action="store_true", help="Skip orchestration")
    
    args = parser.parse_args()
    
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
        model = args.model or ("gpt-4.1-mini" if mode == "eco" else None)
        run_codex_direct(prompt, model=model)
    else:
        run_orchestrator(clean_prompt, mode, args.verbose)


if __name__ == "__main__":
    main()
