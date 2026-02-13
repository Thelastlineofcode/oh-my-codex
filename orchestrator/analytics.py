"""
Analytics engine for Oh My Codex.
Agent performance analysis, model efficiency comparison, and recommendation engine.
"""
from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class AgentPerformanceMetrics:
    """Performance metrics for a single agent role."""
    agent_role: str
    total_actions: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    total_tokens: int = 0
    token_efficiency: float = 0.0  # actions per 1000 tokens


@dataclass
class ModelEfficiency:
    """Efficiency metrics for a model tier."""
    model: str
    total_sessions: int = 0
    total_tokens: int = 0
    avg_tokens_per_session: float = 0.0


@dataclass
class Recommendation:
    """A recommendation from the analytics engine."""
    category: str  # mode, model, agent, optimization
    suggestion: str
    reason: str
    confidence: float = 0.0


@dataclass
class AnalyticsSummary:
    """Complete analytics summary."""
    total_sessions: int = 0
    total_tokens: int = 0
    total_agent_actions: int = 0
    avg_tokens_per_session: float = 0.0
    agent_metrics: list[AgentPerformanceMetrics] = field(default_factory=list)
    model_metrics: list[ModelEfficiency] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    top_agents: list[str] = field(default_factory=list)
    most_used_mode: str = ""


class AnalyticsEngine:
    """Analytics engine for orchestration performance analysis."""

    def __init__(self, state_manager: Any = None) -> None:
        """Initialize with optional StateManager."""
        self._state_manager = state_manager

    def get_agent_metrics(self) -> list[AgentPerformanceMetrics]:
        """Get performance metrics for all agent roles."""
        if self._state_manager is None:
            return []

        stats = self._state_manager.get_agent_stats()
        token_stats = self._state_manager.get_token_stats()

        # Build token lookup
        token_lookup: dict[str, int] = {}
        for ts in token_stats:
            token_lookup[ts["agent_role"]] = ts["total_tokens"]

        metrics = []
        for s in stats:
            role = s["agent_role"]
            total_tokens = token_lookup.get(role, s.get("total_tokens", 0))
            total_actions = s["total_actions"]

            efficiency = 0.0
            if total_tokens > 0:
                efficiency = (total_actions / total_tokens) * 1000

            metrics.append(AgentPerformanceMetrics(
                agent_role=role,
                total_actions=total_actions,
                total_duration=s["total_duration"],
                avg_duration=s["avg_duration"],
                total_tokens=total_tokens,
                token_efficiency=round(efficiency, 2),
            ))

        return sorted(metrics, key=lambda m: m.total_actions, reverse=True)

    def get_model_efficiency(self) -> list[ModelEfficiency]:
        """Get efficiency metrics per mode (proxy for model since modes map to models)."""
        if self._state_manager is None:
            return []

        sessions = self._state_manager.get_all_sessions()

        # Group by mode
        mode_data: dict[str, dict[str, Any]] = {}
        for s in sessions:
            mode = s["mode"]
            if mode not in mode_data:
                mode_data[mode] = {"count": 0, "tokens": 0}
            mode_data[mode]["count"] += 1

        # Get token totals per session
        for s in sessions:
            sid = s["session_id"]
            tokens = self._state_manager.get_session_tokens(sid)
            mode = s["mode"]
            mode_data[mode]["tokens"] += tokens

        metrics = []
        for mode, data in mode_data.items():
            count = data["count"]
            tokens = data["tokens"]
            avg = tokens / count if count > 0 else 0
            metrics.append(ModelEfficiency(
                model=mode,
                total_sessions=count,
                total_tokens=tokens,
                avg_tokens_per_session=round(avg, 1),
            ))

        return sorted(metrics, key=lambda m: m.total_sessions, reverse=True)

    def get_recommendations(self) -> list[Recommendation]:
        """Generate recommendations based on usage patterns."""
        recommendations: list[Recommendation] = []

        if self._state_manager is None:
            recommendations.append(Recommendation(
                category="setup",
                suggestion="Enable state tracking",
                reason="State manager not configured. Run tasks with state tracking enabled for analytics.",
                confidence=1.0,
            ))
            return recommendations

        agent_metrics = self.get_agent_metrics()
        model_metrics = self.get_model_efficiency()

        # Check if there's enough data
        if not agent_metrics and not model_metrics:
            recommendations.append(Recommendation(
                category="data",
                suggestion="Run more sessions",
                reason="Not enough data for meaningful recommendations. Run at least 3 sessions.",
                confidence=1.0,
            ))
            return recommendations

        # Agent efficiency recommendations
        if agent_metrics:
            # Find inefficient agents (low efficiency)
            for m in agent_metrics:
                if m.total_tokens > 1000 and m.token_efficiency < 0.5:
                    recommendations.append(Recommendation(
                        category="agent",
                        suggestion=f"Optimize {m.agent_role} agent",
                        reason=f"{m.agent_role} has low token efficiency ({m.token_efficiency:.2f} actions/1K tokens). Consider using a lighter model tier.",
                        confidence=0.7,
                    ))

            # Find most active agents
            if len(agent_metrics) >= 2:
                top = agent_metrics[0]
                if top.total_actions > agent_metrics[1].total_actions * 3:
                    recommendations.append(Recommendation(
                        category="optimization",
                        suggestion=f"Consider distributing {top.agent_role} workload",
                        reason=f"{top.agent_role} handles {top.total_actions} actions, 3x more than the next agent. Consider task decomposition.",
                        confidence=0.6,
                    ))

        # Mode recommendations
        if model_metrics:
            # Find expensive modes
            for m in model_metrics:
                if m.avg_tokens_per_session > 50000:
                    recommendations.append(Recommendation(
                        category="mode",
                        suggestion=f"Consider eco mode for {m.model} tasks",
                        reason=f"{m.model} mode averages {m.avg_tokens_per_session:.0f} tokens/session. Eco mode could reduce this.",
                        confidence=0.6,
                    ))

            # Suggest ultrawork for users stuck on single modes
            modes_used = {m.model for m in model_metrics}
            if len(modes_used) == 1 and "autopilot" in modes_used:
                recommendations.append(Recommendation(
                    category="mode",
                    suggestion="Try ultrawork for parallel tasks",
                    reason="You only use autopilot mode. For multi-file tasks, ultrawork can be faster.",
                    confidence=0.5,
                ))

        return recommendations

    def get_summary(self) -> AnalyticsSummary:
        """Get a complete analytics summary."""
        agent_metrics = self.get_agent_metrics()
        model_metrics = self.get_model_efficiency()
        recommendations = self.get_recommendations()

        total_sessions = sum(m.total_sessions for m in model_metrics)
        total_tokens = sum(m.total_tokens for m in model_metrics)
        total_actions = sum(m.total_actions for m in agent_metrics)
        avg_tokens = total_tokens / total_sessions if total_sessions > 0 else 0

        top_agents = [m.agent_role for m in agent_metrics[:3]]
        most_used = model_metrics[0].model if model_metrics else ""

        return AnalyticsSummary(
            total_sessions=total_sessions,
            total_tokens=total_tokens,
            total_agent_actions=total_actions,
            avg_tokens_per_session=round(avg_tokens, 1),
            agent_metrics=agent_metrics,
            model_metrics=model_metrics,
            recommendations=recommendations,
            top_agents=top_agents,
            most_used_mode=most_used,
        )

    def export_json(self) -> str:
        """Export analytics as JSON string."""
        summary = self.get_summary()
        data = {
            "total_sessions": summary.total_sessions,
            "total_tokens": summary.total_tokens,
            "total_agent_actions": summary.total_agent_actions,
            "avg_tokens_per_session": summary.avg_tokens_per_session,
            "most_used_mode": summary.most_used_mode,
            "top_agents": summary.top_agents,
            "agent_metrics": [asdict(m) for m in summary.agent_metrics],
            "model_metrics": [asdict(m) for m in summary.model_metrics],
            "recommendations": [asdict(r) for r in summary.recommendations],
        }
        return json.dumps(data, indent=2)

    def export_csv(self) -> str:
        """Export agent metrics as CSV string."""
        metrics = self.get_agent_metrics()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["agent_role", "total_actions", "total_duration", "avg_duration", "total_tokens", "token_efficiency"])
        for m in metrics:
            writer.writerow([m.agent_role, m.total_actions, m.total_duration, m.avg_duration, m.total_tokens, m.token_efficiency])
        return output.getvalue()

    def format_summary(self) -> str:
        """Format summary for terminal display."""
        summary = self.get_summary()

        lines = []
        lines.append("\033[38;5;208m\033[1m  OMX Analytics\033[0m")
        lines.append(f"  \033[2m{'─' * 45}\033[0m")

        # Overview
        lines.append(f"  Sessions: {summary.total_sessions}")
        lines.append(f"  Total Tokens: {self._format_tokens(summary.total_tokens)}")
        lines.append(f"  Avg Tokens/Session: {self._format_tokens(int(summary.avg_tokens_per_session))}")
        lines.append(f"  Agent Actions: {summary.total_agent_actions}")
        if summary.most_used_mode:
            lines.append(f"  Most Used Mode: {summary.most_used_mode}")

        # Agent metrics
        if summary.agent_metrics:
            lines.append(f"\n  \033[1mAgent Performance:\033[0m")
            for m in summary.agent_metrics:
                lines.append(f"    {m.agent_role:<15} {m.total_actions:>4} actions  {m.avg_duration:>6.1f}s avg  {self._format_tokens(m.total_tokens):>8} tokens")

        # Model metrics
        if summary.model_metrics:
            lines.append(f"\n  \033[1mMode Efficiency:\033[0m")
            for m in summary.model_metrics:
                lines.append(f"    {m.model:<15} {m.total_sessions:>4} sessions  {self._format_tokens(m.total_tokens):>8} tokens  {self._format_tokens(int(m.avg_tokens_per_session)):>8}/session")

        # Recommendations
        if summary.recommendations:
            lines.append(f"\n  \033[1mRecommendations:\033[0m")
            for r in summary.recommendations:
                confidence_bar = "●" * int(r.confidence * 5) + "○" * (5 - int(r.confidence * 5))
                lines.append(f"    [{confidence_bar}] {r.suggestion}")
                lines.append(f"    \033[2m{r.reason}\033[0m")

        return "\n".join(lines)

    def _format_tokens(self, count: int) -> str:
        """Format token count."""
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        elif count >= 1_000:
            return f"{count / 1_000:.1f}K"
        return str(count)
