# Release Skill

Version management and release preparation.

## When to Use
- Preparing releases
- Version bumping
- Changelog generation
- Release notes
- Tag management

## Release Process

### 1. Pre-Release Checks
```
□ All tests passing
□ No critical bugs
□ Documentation updated
□ Breaking changes documented
□ Dependencies up to date
```

### 2. Version Bump
```
Semantic Versioning: MAJOR.MINOR.PATCH

MAJOR - Breaking changes
MINOR - New features (backward compatible)
PATCH - Bug fixes (backward compatible)
```

### 3. Changelog Generation
```markdown
## [1.2.0] - 2026-02-13

### Added
- New feature X (#123)
- Support for Y

### Changed
- Improved performance of Z

### Fixed
- Bug in authentication (#456)

### Deprecated
- Old API endpoint (use /v2 instead)

### Removed
- Legacy support for X

### Security
- Updated dependencies
```

### 4. Release Notes
```markdown
# Release 1.2.0

## Highlights
- 🚀 Major performance improvements
- ✨ New dashboard features
- 🔒 Security updates

## Breaking Changes
None in this release.

## Migration Guide
No migration needed.

## Contributors
- @user1
- @user2
```

## Commit Convention

```
feat: new feature
fix: bug fix
docs: documentation
style: formatting
refactor: code restructure
perf: performance
test: testing
chore: maintenance
```

## Usage

```
release: prepare version 1.2.0

release: generate changelog from commits

release: create release notes for v2.0.0
```

## Automation

```bash
# Bump version
npm version minor

# Generate changelog
npx conventional-changelog -p angular -i CHANGELOG.md -s

# Create tag
git tag -a v1.2.0 -m "Release 1.2.0"

# Push with tags
git push origin main --tags
```

## Best Practices

1. **Release often** - Small, frequent releases
2. **Automate** - CI/CD for releases
3. **Document** - Clear changelogs
4. **Communicate** - Notify users of changes
5. **Rollback plan** - Know how to revert
