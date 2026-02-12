"""
Tools for Oh My Codex agents.
Using OpenAI Agents SDK function_tool decorator.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Callable

try:
    from agents import function_tool
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    function_tool = None


def _run_shell(command: str, cwd: str | None = None) -> str:
    """
    Execute a shell command and return output.
    
    Args:
        command: Shell command to execute
        cwd: Working directory (optional)
    
    Returns:
        Command output (stdout + stderr)
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd or os.getcwd(),
            timeout=300,  # 5 minute timeout
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n[EXIT CODE: {result.returncode}]"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "[ERROR] Command timed out after 5 minutes"
    except Exception as e:
        return f"[ERROR] {str(e)}"


def _read_file(path: str) -> str:
    """
    Read contents of a file.
    
    Args:
        path: File path to read
    
    Returns:
        File contents
    """
    try:
        file_path = Path(path).expanduser()
        if not file_path.exists():
            return f"[ERROR] File not found: {path}"
        if file_path.stat().st_size > 1_000_000:  # 1MB limit
            return f"[ERROR] File too large (>1MB): {path}"
        return file_path.read_text()
    except Exception as e:
        return f"[ERROR] {str(e)}"


def _write_file(path: str, content: str) -> str:
    """
    Write content to a file.
    
    Args:
        path: File path to write
        content: Content to write
    
    Returns:
        Success/error message
    """
    try:
        file_path = Path(path).expanduser()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return f"✅ Written {len(content)} bytes to {path}"
    except Exception as e:
        return f"[ERROR] {str(e)}"


def _edit_file(path: str, old_text: str, new_text: str) -> str:
    """
    Replace exact text in a file.
    
    Args:
        path: File path to edit
        old_text: Exact text to find
        new_text: Text to replace with
    
    Returns:
        Success/error message
    """
    try:
        file_path = Path(path).expanduser()
        if not file_path.exists():
            return f"[ERROR] File not found: {path}"
        
        content = file_path.read_text()
        if old_text not in content:
            return f"[ERROR] Text not found in file"
        
        new_content = content.replace(old_text, new_text, 1)
        file_path.write_text(new_content)
        return f"✅ Replaced text in {path}"
    except Exception as e:
        return f"[ERROR] {str(e)}"


def _list_directory(path: str = ".", pattern: str = "*") -> str:
    """
    List files in a directory.
    
    Args:
        path: Directory path
        pattern: Glob pattern (default: *)
    
    Returns:
        List of files
    """
    try:
        dir_path = Path(path).expanduser()
        if not dir_path.exists():
            return f"[ERROR] Directory not found: {path}"
        
        files = sorted(dir_path.glob(pattern))
        result = []
        for f in files[:100]:  # Limit to 100 entries
            prefix = "📁" if f.is_dir() else "📄"
            result.append(f"{prefix} {f.name}")
        
        if len(files) > 100:
            result.append(f"... and {len(files) - 100} more")
        
        return "\n".join(result) or "(empty directory)"
    except Exception as e:
        return f"[ERROR] {str(e)}"


def _search_files(pattern: str, path: str = ".", content_pattern: str | None = None) -> str:
    """
    Search for files by name or content.
    
    Args:
        pattern: Filename glob pattern
        path: Directory to search
        content_pattern: Optional text to search within files
    
    Returns:
        Matching files
    """
    try:
        dir_path = Path(path).expanduser()
        matches = []
        
        for file_path in dir_path.rglob(pattern):
            if file_path.is_file():
                if content_pattern:
                    try:
                        content = file_path.read_text()
                        if content_pattern in content:
                            matches.append(str(file_path))
                    except:
                        pass
                else:
                    matches.append(str(file_path))
            
            if len(matches) >= 50:
                break
        
        if matches:
            result = "\n".join(matches)
            if len(matches) >= 50:
                result += "\n... (truncated at 50 results)"
            return result
        return "(no matches)"
    except Exception as e:
        return f"[ERROR] {str(e)}"


def _git_status() -> str:
    """Get git repository status."""
    return _run_shell("git status --short && echo '---' && git log --oneline -5")


def _git_diff(path: str | None = None) -> str:
    """
    Get git diff for staged or unstaged changes.
    
    Args:
        path: Optional specific file path
    """
    cmd = "git diff"
    if path:
        cmd += f" -- {path}"
    return _run_shell(cmd)


def _run_tests(command: str | None = None) -> str:
    """
    Run tests in the project.
    
    Args:
        command: Test command (auto-detected if not provided)
    """
    if command:
        return _run_shell(command)
    
    # Auto-detect test framework
    cwd = Path.cwd()
    if (cwd / "package.json").exists():
        return _run_shell("npm test")
    elif (cwd / "pytest.ini").exists() or (cwd / "pyproject.toml").exists():
        return _run_shell("pytest -v")
    elif (cwd / "Cargo.toml").exists():
        return _run_shell("cargo test")
    elif (cwd / "go.mod").exists():
        return _run_shell("go test ./...")
    else:
        return "[ERROR] Could not auto-detect test framework"


# Raw function references (for testing)
run_shell = _run_shell
read_file = _read_file
write_file = _write_file
edit_file = _edit_file
list_directory = _list_directory
search_files = _search_files
git_status = _git_status
git_diff = _git_diff
run_tests = _run_tests

# Wrapped tools for SDK (only if available)
if TOOLS_AVAILABLE and function_tool:
    run_shell_tool = function_tool(_run_shell)
    read_file_tool = function_tool(_read_file)
    write_file_tool = function_tool(_write_file)
    edit_file_tool = function_tool(_edit_file)
    list_directory_tool = function_tool(_list_directory)
    search_files_tool = function_tool(_search_files)
    git_status_tool = function_tool(_git_status)
    git_diff_tool = function_tool(_git_diff)
    run_tests_tool = function_tool(_run_tests)
    
    ALL_TOOLS = [
        run_shell_tool,
        read_file_tool,
        write_file_tool,
        edit_file_tool,
        list_directory_tool,
        search_files_tool,
        git_status_tool,
        git_diff_tool,
        run_tests_tool,
    ]
    
    BASIC_TOOLS = [
        read_file_tool,
        list_directory_tool,
        search_files_tool,
        git_status_tool,
    ]
else:
    ALL_TOOLS = [
        _run_shell,
        _read_file,
        _write_file,
        _edit_file,
        _list_directory,
        _search_files,
        _git_status,
        _git_diff,
        _run_tests,
    ]
    
    BASIC_TOOLS = [
        _read_file,
        _list_directory,
        _search_files,
        _git_status,
    ]


def get_tools_for_role(role: str) -> list:
    """Get appropriate tools for an agent role."""
    # Execution-capable roles get all tools
    execution_roles = [
        "pm", "executor", "deep-executor", "frontend", "backend",
        "fullstack", "mobile", "devops", "tester", "debugger",
        "refactorer", "migrator"
    ]
    
    if role in execution_roles:
        return ALL_TOOLS
    
    # Read-only roles get basic tools
    return BASIC_TOOLS
