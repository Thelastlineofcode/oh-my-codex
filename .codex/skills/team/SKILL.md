# Team Skill

Canonical multi-agent orchestration with staged pipeline.

## When to Use
- Complex features requiring multiple specialists
- Coordinated parallel work
- Tasks needing plan → execute → verify cycles
- Team-based development workflows

## When NOT to Use
- Simple single-file changes
- Quick fixes (use eco)
- Solo exploration tasks

## Pipeline Stages

```
team-plan → team-prd → team-exec → team-verify → team-fix (loop)
```

### 1. team-plan
- Analyze task requirements
- Break into workstreams
- Assign agent roles

### 2. team-prd
- Create detailed specifications
- Define acceptance criteria
- Document dependencies

### 3. team-exec
- Execute in parallel
- Coordinate between agents
- Track progress

### 4. team-verify
- Run tests
- Check acceptance criteria
- Validate integration

### 5. team-fix (loop)
- Address failures
- Iterate until passing
- Max 3 fix attempts

## Agent Assignment

```
Task Type           → Primary Agent    → Support Agents
────────────────────────────────────────────────────────
Feature Development → Fullstack        → Frontend, Backend, Tester
API Design          → Backend          → Architect, Docs
UI Implementation   → Frontend         → Designer, Tester
Bug Investigation   → Debugger         → Analyst, Tester
Refactoring         → Refactorer       → Reviewer, Tester
Security Audit      → Security         → Reviewer, Analyst
```

## Usage

```
team: build a user dashboard with analytics

team 3:executor fix all TypeScript errors

team: implement payment processing with Stripe
```

## Configuration

Agents communicate through shared task lists and can:
- Read/write to shared documents
- Signal completion or blockers
- Request help from other agents
