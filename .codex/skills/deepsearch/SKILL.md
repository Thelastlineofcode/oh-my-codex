# Deepsearch Skill

Deep codebase exploration and understanding.

## When to Use
- Understanding unfamiliar codebases
- Finding specific implementations
- Tracing data flow
- Mapping dependencies
- Onboarding to projects

## When NOT to Use
- When you already know the location
- Simple file lookups

## Search Capabilities

### Structural Search
```
Find all:
- Components that use a specific hook
- Functions that call an API
- Classes that implement an interface
- Files that import a module
```

### Semantic Search
```
Find code that:
- Handles authentication
- Processes payments
- Validates user input
- Manages state
```

### Pattern Search
```
Find patterns:
- N+1 query potential
- Unused exports
- Circular dependencies
- Code duplication
```

## Exploration Strategies

### Top-Down
```
Entry point → Main modules → Sub-modules → Details
```

### Bottom-Up
```
Specific function → Callers → Higher-level usage
```

### Data Flow
```
Input → Transformations → Output
```

### Dependency Graph
```
Module → Imports → Transitive dependencies
```

## Output Format

```markdown
## Codebase Analysis: {scope}

### Structure Overview
```
src/
├── components/     # React components
├── hooks/          # Custom hooks
├── services/       # API services
├── utils/          # Utilities
└── types/          # TypeScript types
```

### Key Files
| File | Purpose | Dependencies |
|------|---------|--------------|
| auth.ts | Authentication | api, storage |
| api.ts | HTTP client | axios |

### Data Flow
User Input → Validation → API Call → State Update → UI Render

### Findings
1. {finding 1}
2. {finding 2}

### Recommendations
- {recommendation}
```

## Usage

```
deepsearch: how does authentication work in this codebase

deepsearch: find all places that handle payment processing

deepsearch: map the data flow for user registration
```

## Tips

1. **Start broad, narrow down** - Overview first, then details
2. **Follow the data** - Trace from input to output
3. **Check tests** - Tests reveal expected behavior
4. **Read types first** - TypeScript types document structure
