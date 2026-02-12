# Planner Skill

Interview-driven planning for complex projects.

## When to Use
- Starting a new project
- Major architectural decisions
- Unclear or ambiguous requirements
- When user says "plan" or wants to think before doing

## When NOT to Use
- Simple, well-defined tasks
- Urgent fixes
- When user explicitly wants immediate action
- Follow-up work on existing plans

## Workflow

```
1. INTERVIEW
   - Ask 3-5 clarifying questions
   - Understand constraints and preferences
   - Identify non-obvious requirements

2. SYNTHESIZE
   - Summarize understanding
   - Confirm with user before proceeding

3. ARCHITECT
   - Design high-level structure
   - Identify components and relationships
   - Choose patterns and technologies

4. DECOMPOSE
   - Break into phases
   - Define milestones
   - Estimate effort

5. DOCUMENT
   - Save to .codex/plans/{project-name}.md
   - Include decision rationale
```

## Interview Questions Template

Ask in order of importance, stop when you have enough:

1. **Goal**: "What's the end result you're looking for?"
2. **Context**: "What existing code/systems does this interact with?"
3. **Constraints**: "Any tech stack requirements or limitations?"
4. **Timeline**: "Is this urgent or can we iterate?"
5. **Quality**: "What's more important - speed or polish?"

## Plan Document Structure

```markdown
# Project: {name}
Date: {date}
Status: Planning | In Progress | Complete

## Overview
{2-3 sentence summary}

## Requirements
### Must Have
- {requirement}

### Nice to Have
- {requirement}

## Architecture
{diagram or description}

## Phases
### Phase 1: {name}
- {task}
- {task}
Milestone: {what's done when phase completes}

### Phase 2: {name}
...

## Tech Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| {what} | {choice} | {why} |

## Risks
- {risk}: {mitigation}

## Open Questions
- {question}
```

## Examples

**Good trigger:**
> "plan: I want to build a CLI tool for managing my dotfiles"

**Good trigger:**
> "Let's think through how to architect the payment system"

**Bad trigger:**
> "plan: fix the bug" (too simple, just fix it)
