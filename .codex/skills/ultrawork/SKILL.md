# Ultrawork Skill (ulw)

Parallel execution mode for large-scale multi-file operations.

## When to Use
- Refactoring across 5+ files
- Bulk updates (imports, naming conventions)
- Parallel feature development (independent components)
- Large codebase migrations

## When NOT to Use
- Sequential dependencies between changes
- Single-file modifications
- Tasks requiring careful ordering
- When changes might conflict

## Workflow

```
1. DECOMPOSE
   - Identify independent work units
   - Group by file/module boundaries
   - Check for conflicts between units

2. PARALLELIZE
   - Spawn sub-tasks (conceptually parallel)
   - Each unit gets isolated context
   - No cross-unit dependencies allowed

3. AGGREGATE
   - Collect all results
   - Check for merge conflicts
   - Resolve any inconsistencies

4. VERIFY
   - Run full test suite
   - Check for broken imports
   - Validate integration points
```

## Decomposition Rules

```
INDEPENDENT if:
- Different files with no shared imports
- Same file, different functions (careful!)
- Different modules entirely

DEPENDENT if:
- Shared type definitions
- Import/export relationships
- Shared state or config
```

## Task Unit Template

```markdown
## Unit: {name}
Files: {file1}, {file2}
Action: {what to do}
Isolated: {yes/no}
Conflicts with: {none | unit names}
```

## Execution Strategy

For truly parallel work with Codex MCP:
```python
# Conceptual - actual implementation in orchestrator/
async def ultrawork(units):
    tasks = [spawn_codex_session(unit) for unit in units]
    results = await asyncio.gather(*tasks)
    return merge_results(results)
```

## Examples

**Good trigger:**
> "ulw: rename all instances of 'userId' to 'user_id' across the codebase"

**Good trigger:**
> "ulw: add TypeScript types to all utility functions"

**Bad trigger:**
> "ulw: refactor the auth module" (likely has dependencies)
