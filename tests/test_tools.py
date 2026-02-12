"""Tests for tools module."""

import pytest
import tempfile
import os
from pathlib import Path

from orchestrator.tools import (
    run_shell,
    read_file,
    write_file,
    edit_file,
    list_directory,
    search_files,
    get_tools_for_role,
    ALL_TOOLS,
)


class TestRunShell:
    """Tests for run_shell tool."""
    
    def test_simple_command(self):
        """Execute a simple command."""
        result = run_shell("echo hello")
        assert "hello" in result
    
    def test_command_with_error(self):
        """Handle command errors."""
        result = run_shell("exit 1")
        assert "EXIT CODE: 1" in result
    
    def test_nonexistent_command(self):
        """Handle nonexistent commands."""
        result = run_shell("nonexistent_command_xyz")
        assert "not found" in result.lower() or "ERROR" in result or "EXIT CODE" in result


class TestReadFile:
    """Tests for read_file tool."""
    
    def test_read_existing_file(self):
        """Read an existing file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            f.flush()
            result = read_file(f.name)
            assert result == "test content"
            os.unlink(f.name)
    
    def test_read_nonexistent_file(self):
        """Handle nonexistent file."""
        result = read_file("/nonexistent/path/file.txt")
        assert "ERROR" in result


class TestWriteFile:
    """Tests for write_file tool."""
    
    def test_write_new_file(self):
        """Write a new file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.txt")
            result = write_file(path, "hello world")
            assert "✅" in result
            assert Path(path).read_text() == "hello world"
    
    def test_write_creates_dirs(self):
        """Write creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "nested", "dir", "test.txt")
            result = write_file(path, "content")
            assert "✅" in result
            assert Path(path).exists()


class TestEditFile:
    """Tests for edit_file tool."""
    
    def test_edit_existing_content(self):
        """Edit existing content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("hello world")
            f.flush()
            result = edit_file(f.name, "world", "universe")
            assert "✅" in result
            assert Path(f.name).read_text() == "hello universe"
            os.unlink(f.name)
    
    def test_edit_nonexistent_text(self):
        """Handle text not found."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("hello world")
            f.flush()
            result = edit_file(f.name, "xyz", "abc")
            assert "ERROR" in result
            os.unlink(f.name)


class TestListDirectory:
    """Tests for list_directory tool."""
    
    def test_list_current_dir(self):
        """List current directory."""
        result = list_directory(".")
        assert len(result) > 0
    
    def test_list_with_pattern(self):
        """List with glob pattern."""
        result = list_directory(".", "*.py")
        # Should filter to .py files only
        assert "📄" in result or "(empty directory)" in result


class TestSearchFiles:
    """Tests for search_files tool."""
    
    def test_search_by_name(self):
        """Search files by name."""
        result = search_files("*.py", ".")
        # Should find Python files
        assert ".py" in result or "(no matches)" in result


class TestGetToolsForRole:
    """Tests for get_tools_for_role."""
    
    def test_executor_gets_all_tools(self):
        """Executor role gets all tools."""
        tools = get_tools_for_role("executor")
        assert len(tools) == len(ALL_TOOLS)
    
    def test_analyst_gets_basic_tools(self):
        """Analyst role gets basic tools only."""
        tools = get_tools_for_role("analyst")
        assert len(tools) < len(ALL_TOOLS)
