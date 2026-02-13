"""Tests for context module."""
import pytest
import json
import tempfile
import shutil
import time
from pathlib import Path
from orchestrator.context import ContextManager, MemoryScope, MemoryPriority, MemoryEntry


@pytest.fixture
def temp_ctx_dir():
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)

@pytest.fixture
def ctx(temp_ctx_dir):
    return ContextManager(storage_dir=temp_ctx_dir)


class TestMemoryEntry:
    def test_create(self):
        e = MemoryEntry(key="k", value="v")
        assert not e.is_expired()

    def test_create_with_defaults(self):
        entry = MemoryEntry(key="test", value="hello")
        assert entry.key == "test"
        assert entry.value == "hello"
        assert entry.scope == MemoryScope.SESSION
        assert entry.priority == MemoryPriority.NORMAL
        assert entry.tags == []
        assert entry.created_at == 0.0
        assert entry.expires_at == 0.0

    def test_expired(self):
        e = MemoryEntry(key="k", value="v", expires_at=time.time() - 10)
        assert e.is_expired()

    def test_is_expired_never_expires(self):
        entry = MemoryEntry(key="k", value="v", expires_at=0)
        assert entry.is_expired() is False

    def test_permanent_never_expires(self):
        e = MemoryEntry(key="k", value="v", priority=MemoryPriority.PERMANENT, expires_at=1.0)
        assert not e.is_expired()

    def test_is_expired_not_yet(self):
        entry = MemoryEntry(key="k", value="v", expires_at=time.time() + 1000)
        assert entry.is_expired() is False

    def test_to_dict(self):
        entry = MemoryEntry(
            key="test",
            value="data",
            scope=MemoryScope.GLOBAL,
            priority=MemoryPriority.HIGH,
            tags=["tag1", "tag2"],
            created_at=123.45,
            expires_at=678.90,
        )
        d = entry.to_dict()
        assert d["key"] == "test"
        assert d["value"] == "data"
        assert d["scope"] == "global"
        assert d["priority"] == "high"
        assert d["tags"] == ["tag1", "tag2"]
        assert d["created_at"] == 123.45
        assert d["expires_at"] == 678.90

    def test_from_dict(self):
        d = {
            "key": "k",
            "value": "v",
            "scope": "session",
            "priority": "normal",
            "tags": ["a"],
            "created_at": 111.0,
            "expires_at": 222.0,
        }
        entry = MemoryEntry.from_dict(d)
        assert entry.key == "k"
        assert entry.value == "v"
        assert entry.scope == MemoryScope.SESSION
        assert entry.priority == MemoryPriority.NORMAL
        assert entry.tags == ["a"]

    def test_from_dict_defaults(self):
        entry = MemoryEntry.from_dict({"key": "k", "value": "v"})
        assert entry.scope == MemoryScope.SESSION
        assert entry.priority == MemoryPriority.NORMAL

    def test_to_from_dict(self):
        e = MemoryEntry(key="k", value="v", tags=["t"])
        d = e.to_dict()
        e2 = MemoryEntry.from_dict(d)
        assert e2.key == "k"
        assert e2.tags == ["t"]

    def test_roundtrip(self):
        original = MemoryEntry(
            key="roundtrip",
            value="test",
            scope=MemoryScope.GLOBAL,
            priority=MemoryPriority.PERMANENT,
            tags=["x", "y"],
        )
        restored = MemoryEntry.from_dict(original.to_dict())
        assert restored.key == original.key
        assert restored.value == original.value
        assert restored.scope == original.scope
        assert restored.priority == original.priority
        assert restored.tags == original.tags


class TestMemoryScope:
    def test_session_value(self):
        assert MemoryScope.SESSION.value == "session"

    def test_global_value(self):
        assert MemoryScope.GLOBAL.value == "global"


class TestMemoryPriority:
    def test_normal_value(self):
        assert MemoryPriority.NORMAL.value == "normal"

    def test_high_value(self):
        assert MemoryPriority.HIGH.value == "high"

    def test_permanent_value(self):
        assert MemoryPriority.PERMANENT.value == "permanent"


class TestContextManager:
    def test_remember_recall(self, ctx):
        ctx.remember("key1", "value1")
        assert ctx.recall("key1") == "value1"

    def test_remember_session(self, ctx):
        entry = ctx.remember("key1", "value1")
        assert entry.key == "key1"
        assert entry.scope == MemoryScope.SESSION

    def test_recall_session(self, ctx):
        ctx.remember("key1", "value1")
        value = ctx.recall("key1")
        assert value == "value1"

    def test_recall_missing(self, ctx):
        assert ctx.recall("nope") is None

    def test_recall_nonexistent(self, ctx):
        assert ctx.recall("nope") is None

    def test_remember_global(self, ctx):
        entry = ctx.remember("gkey", "gval", scope=MemoryScope.GLOBAL)
        assert entry.scope == MemoryScope.GLOBAL
        value = ctx.recall("gkey")
        assert value == "gval"

    def test_global_persists(self, temp_ctx_dir):
        mgr1 = ContextManager(storage_dir=temp_ctx_dir)
        mgr1.remember("persist", "data", scope=MemoryScope.GLOBAL)
        mgr2 = ContextManager(storage_dir=temp_ctx_dir)
        assert mgr2.recall("persist") == "data"

    def test_forget(self, ctx):
        ctx.remember("k", "v")
        assert ctx.forget("k") is True
        assert ctx.recall("k") is None

    def test_forget_session(self, ctx):
        ctx.remember("s", "val")
        assert ctx.forget("s") is True
        assert ctx.recall("s") is None

    def test_forget_global(self, ctx):
        ctx.remember("g", "val", scope=MemoryScope.GLOBAL)
        assert ctx.forget("g") is True
        assert ctx.recall("g") is None

    def test_forget_missing(self, ctx):
        assert ctx.forget("nope") is False

    def test_forget_nonexistent(self, ctx):
        assert ctx.forget("nope") is False

    def test_global_memory_persists(self, temp_ctx_dir):
        ctx1 = ContextManager(storage_dir=temp_ctx_dir)
        ctx1.remember("gk", "gv", scope=MemoryScope.GLOBAL)
        ctx2 = ContextManager(storage_dir=temp_ctx_dir)
        assert ctx2.recall("gk") == "gv"

    def test_session_memory_not_persisted_automatically(self, temp_ctx_dir):
        ctx1 = ContextManager(storage_dir=temp_ctx_dir)
        ctx1.remember("sk", "sv", scope=MemoryScope.SESSION)
        ctx2 = ContextManager(storage_dir=temp_ctx_dir)
        assert ctx2.recall("sk") is None

    def test_save_load_session(self, ctx):
        ctx.remember("s1", "v1")
        ctx.remember("s2", "v2")
        ctx.save_session("test-sess")
        ctx.clear_session()
        assert ctx.recall("s1") is None
        count = ctx.load_session("test-sess")
        assert count == 2
        assert ctx.recall("s1") == "v1"

    def test_save_session(self, ctx, temp_ctx_dir):
        ctx.remember("s1", "val1")
        ctx.remember("s2", "val2")
        assert ctx.save_session("sess-123") is True
        session_file = temp_ctx_dir / "session_sess-123.json"
        assert session_file.exists()
        data = json.loads(session_file.read_text())
        assert len(data["entries"]) == 2

    def test_load_session(self, ctx, temp_ctx_dir):
        ctx.remember("load1", "v1")
        ctx.save_session("sess-load")
        ctx.clear_session()
        assert ctx.recall("load1") is None
        count = ctx.load_session("sess-load")
        assert count == 1
        assert ctx.recall("load1") == "v1"

    def test_load_nonexistent_session(self, ctx):
        count = ctx.load_session("nope")
        assert count == 0

    def test_clear_session(self, ctx):
        ctx.remember("a", "1")
        ctx.remember("b", "2")
        ctx.clear_session()
        assert ctx.recall("a") is None
        assert ctx.recall("b") is None

    def test_search_by_query(self, ctx):
        ctx.remember("auth_token", "abc123")
        ctx.remember("db_host", "localhost")
        ctx.remember("car", "vehicle")
        results = ctx.search("auth")
        assert len(results) == 1

    def test_search_by_tags(self, ctx):
        ctx.remember("k1", "v1", tags=["important"])
        ctx.remember("k2", "v2", tags=["debug", "important"])
        ctx.remember("k3", "v3", tags=["prod"])
        results = ctx.search(tags=["important"])
        assert len(results) == 2

    def test_search_by_scope(self, ctx):
        ctx.remember("s", "v", scope=MemoryScope.SESSION)
        ctx.remember("g", "v", scope=MemoryScope.GLOBAL)
        results = ctx.search(scope=MemoryScope.SESSION)
        assert len(results) == 1
        assert results[0].key == "s"

    def test_search_empty(self, ctx):
        results = ctx.search("zzzzz")
        assert len(results) == 0

    def test_context_injection(self, ctx):
        ctx.remember("k1", "v1", priority=MemoryPriority.PERMANENT)
        ctx.remember("k2", "v2", priority=MemoryPriority.NORMAL)
        output = ctx.get_context_injection()
        assert "k1" in output
        assert "k2" in output

    def test_get_context_injection_ordering(self, ctx):
        ctx.remember("normal", "n", priority=MemoryPriority.NORMAL)
        ctx.remember("high", "h", priority=MemoryPriority.HIGH)
        ctx.remember("perm", "p", priority=MemoryPriority.PERMANENT)
        ctx_str = ctx.get_context_injection()
        lines = ctx_str.split("\n")
        assert "[P]" in lines[0]

    def test_ttl(self, ctx):
        ctx.remember("temp", "val", ttl_seconds=0.01)
        time.sleep(0.02)
        assert ctx.recall("temp") is None

    def test_remember_with_ttl(self, ctx):
        entry = ctx.remember("ttl", "val", ttl_seconds=100)
        assert entry.expires_at > 0
        assert ctx.recall("ttl") == "val"

    def test_recall_expired_auto_removes(self, ctx):
        ctx.remember("exp", "val", ttl_seconds=0.001)
        time.sleep(0.01)
        assert ctx.recall("exp") is None

    def test_cleanup_expired(self, ctx):
        ctx.remember("temp", "val", ttl_seconds=0.01)
        ctx.remember("valid", "new", ttl_seconds=1000)
        time.sleep(0.02)
        removed = ctx.cleanup_expired()
        assert removed >= 1
        assert ctx.recall("valid") == "new"

    def test_session_before_global_in_recall(self, ctx):
        ctx.remember("dup", "session_val", scope=MemoryScope.SESSION)
        ctx.remember("dup", "global_val", scope=MemoryScope.GLOBAL)
        assert ctx.recall("dup") == "session_val"
