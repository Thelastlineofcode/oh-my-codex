# Git Master Skill

Expert git workflow management.

## When to Use
- Complex git operations (rebase, cherry-pick, bisect)
- Branch management strategies
- Commit message crafting
- Merge conflict resolution
- Git history cleanup

## When NOT to Use
- Simple add/commit/push (just do it directly)
- Basic branch checkout

## Capabilities

### Commit Crafting
```
Format: <type>(<scope>): <description>

Types:
- feat: New feature
- fix: Bug fix
- refactor: Code change that neither fixes a bug nor adds a feature
- docs: Documentation only
- test: Adding/updating tests
- chore: Maintenance tasks
- perf: Performance improvement
- style: Code style (formatting, semicolons, etc)

Examples:
feat(auth): add JWT refresh token support
fix(api): handle null user in profile endpoint
refactor(utils): extract date formatting to helper
```

### Branch Strategies

**Feature Branch:**
```bash
git checkout -b feature/description
# work...
git commit -m "feat: ..."
git push -u origin feature/description
# create PR
```

**Hotfix:**
```bash
git checkout -b hotfix/description main
# fix...
git commit -m "fix: ..."
git checkout main && git merge hotfix/description
git tag -a v1.0.1 -m "Hotfix: description"
```

### Interactive Rebase
```bash
# Clean up last N commits
git rebase -i HEAD~N

# Commands:
# pick = keep commit
# reword = change message
# squash = merge into previous
# drop = remove commit
```

### Conflict Resolution
```
1. Identify conflicting files: git status
2. Open each file, look for <<<<<<< markers
3. Choose correct version or merge manually
4. git add <resolved-files>
5. git rebase --continue (or git merge --continue)
```

### Useful Commands
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Stash with message
git stash push -m "description"

# Find commit that introduced bug
git bisect start
git bisect bad HEAD
git bisect good <known-good-commit>

# Cherry-pick specific commit
git cherry-pick <commit-hash>

# View file at specific commit
git show <commit>:<file>
```

## Commit Message Guidelines

1. **Subject line**: Max 50 chars, imperative mood
2. **Body** (optional): Wrap at 72 chars, explain what and why
3. **Footer** (optional): Reference issues, breaking changes

```
fix(auth): prevent session hijacking on logout

The previous implementation didn't invalidate server-side sessions,
allowing stolen tokens to remain valid. Now we:
- Invalidate session in Redis on logout
- Add token to blocklist until expiry

Fixes #123
BREAKING CHANGE: logout now requires valid token
```
