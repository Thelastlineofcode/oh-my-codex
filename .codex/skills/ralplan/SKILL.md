# Ralplan Skill

Iterative planning with consensus building.

## When to Use
- Complex features needing multiple perspectives
- Architecture decisions with tradeoffs
- When initial plan might miss considerations
- Collaborative design sessions

## How It Works

```
Round 1: Initial Plan
    │
    ▼
Round 2: Critique & Improve
    │
    ▼
Round 3: Refine & Validate
    │
    ▼
Consensus Reached → Execute
```

## Process

### Round 1: Draft
```
Planner creates initial plan:
- Goals
- Approach
- Tasks
- Estimates
```

### Round 2: Critique
```
Critic reviews and challenges:
- Missing considerations?
- Better alternatives?
- Risks not addressed?
- Complexity concerns?
```

### Round 3: Refine
```
Planner incorporates feedback:
- Address critiques
- Add missing pieces
- Simplify where possible
- Finalize plan
```

### Consensus Check
```
Both agents agree:
- Plan is complete
- Risks are mitigated
- Approach is sound
→ Ready for execution
```

## Usage

```
ralplan: design the notification system

ralplan: architect the payment integration

ralplan this feature before implementing
```

## Output

```markdown
## Ralplan: {Feature}

### Round 1: Initial Plan
{Planner's draft}

### Round 2: Critique
{Critic's feedback}
- ⚠️ {concern 1}
- ⚠️ {concern 2}
- 💡 {suggestion}

### Round 3: Refined Plan
{Improved plan addressing feedback}

### Consensus
✅ Both agents agree on final plan

### Final Plan
{Ready for execution}
```

## Benefits

1. **Multiple perspectives** - Catches blind spots
2. **Stress-tested** - Plan survives criticism
3. **Better estimates** - More realistic after critique
4. **Documented reasoning** - Know why decisions were made
