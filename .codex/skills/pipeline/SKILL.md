# Pipeline Skill

Sequential, staged processing for multi-step transformations.

## When to Use
- Multi-step data transformations
- Sequential processing with dependencies
- Workflows with strict ordering
- Build/deploy pipelines

## When NOT to Use
- Independent parallel tasks (use ultrawork)
- Simple single-step operations
- Tasks without dependencies

## Pipeline Concept

```
Stage 1 → Stage 2 → Stage 3 → Stage 4 → Output
   │         │         │         │
   └─────────┴─────────┴─────────┘
         Each stage depends on previous
```

## Pipeline Definition

```yaml
pipeline:
  name: "Feature Implementation"
  stages:
    - name: plan
      agent: planner
      input: user_request
      output: plan_document
      
    - name: implement
      agent: executor
      input: plan_document
      output: code_changes
      
    - name: test
      agent: tester
      input: code_changes
      output: test_results
      
    - name: review
      agent: reviewer
      input: code_changes
      output: review_feedback
      
    - name: document
      agent: writer
      input: code_changes
      output: documentation
```

## Stage Types

### Transform
```
Input → Processing → Output
```

### Validate
```
Input → Check → Pass/Fail
```

### Branch
```
Input → Condition → Path A or Path B
```

### Aggregate
```
Multiple Inputs → Combine → Single Output
```

## Built-in Pipelines

### Feature Pipeline
```
plan → implement → test → review → document → deploy
```

### Bug Fix Pipeline
```
reproduce → diagnose → fix → test → review
```

### Refactor Pipeline
```
analyze → plan → refactor → test → review
```

### Migration Pipeline
```
assess → plan → migrate → verify → cleanup
```

## Usage

```
pipeline: implement user authentication
  - plan the feature
  - implement backend
  - implement frontend
  - write tests
  - document API

pipeline: migrate from REST to GraphQL
```

## Error Handling

```
On stage failure:
1. Log error context
2. Attempt retry (configurable)
3. If still failing:
   - Option A: Stop pipeline
   - Option B: Skip to next stage
   - Option C: Rollback previous stages
```

## Pipeline Visualization

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  Plan   │───▶│ Execute │───▶│  Test   │───▶│ Review  │
│    ✓    │    │    ✓    │    │   ...   │    │         │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
   2min           15min          5min           -
```
