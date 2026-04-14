# oh-my-codex — AGENTS.md

> ANN-Mesh parity repo. Canonical system spec: https://github.com/Thelastlineofcode/ANN-Mesh/blob/main/AGENTS.md

## Role in ANN-Mesh
Multi-agent orchestration reference — `orchestrator/`, `AGENTS.md`, `config.yaml` patterns.
Skill file: `.ann-core/skills/multi-agent-orchestration.md`
Primary agents: **Ann** (orchestration patterns) · **Scooter** (implementation)

## Key Rules
- Load `multi-agent-orchestration.md` skill before operating
- Boot: `ann health` → `ann context hydrate --agent ann-agent-ann`
- No self-merges. Scooter opens PRs. Roids gates.

## Connections
- rickd: `http://localhost:8080`
- ANN-Mesh: https://github.com/Thelastlineofcode/ANN-Mesh
