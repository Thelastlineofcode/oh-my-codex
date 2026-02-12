# Learner Skill

Extract and reuse problem-solving patterns.

## When to Use
- After solving complex problems
- Building personal knowledge base
- Creating reusable solutions
- Documenting lessons learned

## How It Works

```
Problem → Solution → Pattern Extraction → Knowledge Base
                           │
                           ▼
                    Future Problems
```

## Pattern Categories

### Code Patterns
```yaml
pattern:
  name: "Retry with Exponential Backoff"
  category: resilience
  problem: "API calls failing intermittently"
  solution: |
    async function retryWithBackoff(fn, maxRetries = 3) {
      for (let i = 0; i < maxRetries; i++) {
        try {
          return await fn();
        } catch (e) {
          if (i === maxRetries - 1) throw e;
          await sleep(Math.pow(2, i) * 1000);
        }
      }
    }
  when_to_use:
    - Unreliable external APIs
    - Network instability
    - Rate limiting
  when_not_to_use:
    - User-facing synchronous operations
    - Non-idempotent operations
```

### Architecture Patterns
```yaml
pattern:
  name: "Repository Pattern"
  category: architecture
  problem: "Direct database access scattered in code"
  solution: "Abstract data access behind repository interfaces"
  benefits:
    - Testability
    - Swappable implementations
    - Centralized queries
```

### Debugging Patterns
```yaml
pattern:
  name: "Binary Search Debugging"
  category: debugging
  problem: "Bug in large codebase"
  solution: |
    1. Identify working state (git bisect good)
    2. Identify broken state (git bisect bad)
    3. Binary search through commits
    4. Find exact commit that introduced bug
```

## Learning Process

### 1. Capture
```markdown
## Problem
{What was the issue?}

## Context
{What were the constraints?}

## Solution
{How did you solve it?}

## Key Insight
{What was the "aha" moment?}

## Reusability
{When would this apply again?}
```

### 2. Generalize
```
Specific Solution → Abstract Pattern → Reusable Template
```

### 3. Store
```
~/.codex/patterns/
├── code/
├── architecture/
├── debugging/
└── workflow/
```

### 4. Recall
```
When facing new problem:
1. Match against pattern categories
2. Retrieve relevant patterns
3. Adapt to current context
```

## Usage

```
learner: extract pattern from this auth implementation

learner: save this debugging approach for future reference

learner: what patterns do I have for handling rate limits?
```

## Pattern Template

```markdown
# Pattern: {Name}

## Category
{code|architecture|debugging|workflow}

## Problem
{What problem does this solve?}

## Solution
{The pattern/approach}

## Example
{Concrete implementation}

## When to Use
- {condition 1}
- {condition 2}

## When NOT to Use
- {anti-condition}

## Related Patterns
- {related pattern}

## References
- {source}
```
