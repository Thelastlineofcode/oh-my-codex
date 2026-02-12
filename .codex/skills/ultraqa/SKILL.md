# UltraQA Skill

Comprehensive quality assurance with parallel testing.

## When to Use
- Full test suite execution
- Quality gates before release
- Regression testing
- Test coverage improvement
- Bug hunting sessions

## Testing Pyramid

```
        ╱╲
       ╱  ╲
      ╱ E2E╲        Few, slow, high confidence
     ╱──────╲
    ╱ Integ. ╲      Some, medium speed
   ╱──────────╲
  ╱   Unit     ╲    Many, fast, focused
 ╱──────────────╲
```

## Test Categories

### Unit Tests
```typescript
describe('calculateTotal', () => {
  it('should sum items correctly', () => {
    expect(calculateTotal([10, 20, 30])).toBe(60);
  });

  it('should handle empty array', () => {
    expect(calculateTotal([])).toBe(0);
  });

  it('should handle negative numbers', () => {
    expect(calculateTotal([10, -5])).toBe(5);
  });
});
```

### Integration Tests
```typescript
describe('User API', () => {
  it('should create and retrieve user', async () => {
    const created = await api.createUser({ name: 'Test' });
    const retrieved = await api.getUser(created.id);
    expect(retrieved.name).toBe('Test');
  });
});
```

### E2E Tests
```typescript
test('user can complete checkout', async ({ page }) => {
  await page.goto('/products');
  await page.click('[data-testid="add-to-cart"]');
  await page.click('[data-testid="checkout"]');
  await page.fill('#email', 'test@example.com');
  await page.click('[data-testid="place-order"]');
  await expect(page.locator('.success')).toBeVisible();
});
```

## Quality Checks

### Code Quality
```
□ All tests passing
□ Coverage > 80%
□ No lint errors
□ No type errors
□ No security vulnerabilities
```

### Performance
```
□ Load time < 3s
□ API response < 200ms
□ No memory leaks
□ Bundle size acceptable
```

### Accessibility
```
□ WCAG 2.1 AA compliant
□ Keyboard navigable
□ Screen reader compatible
□ Color contrast sufficient
```

## Parallel Testing

```
┌────────────────────────────────────────┐
│           UltraQA Orchestrator          │
├────────────────────────────────────────┤
│                                         │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│   │ Unit    │ │ Integ   │ │ E2E     │  │
│   │ Tests   │ │ Tests   │ │ Tests   │  │
│   │ (fast)  │ │ (med)   │ │ (slow)  │  │
│   └────┬────┘ └────┬────┘ └────┬────┘  │
│        │           │           │        │
│        └───────────┴───────────┘        │
│                    │                    │
│              ┌─────▼─────┐              │
│              │  Report   │              │
│              │  & Merge  │              │
│              └───────────┘              │
│                                         │
└────────────────────────────────────────┘
```

## Usage

```
ultraqa: run full test suite with coverage report

ultraqa: comprehensive QA check before release

ultraqa: find and fix all failing tests
```

## Output Format

```markdown
## QA Report

### Test Results
| Suite | Passed | Failed | Skipped | Coverage |
|-------|--------|--------|---------|----------|
| Unit  | 142    | 0      | 2       | 87%      |
| Integ | 45     | 1      | 0       | 72%      |
| E2E   | 23     | 0      | 0       | N/A      |

### Failed Tests
1. `integration/api.test.ts` - User creation timeout

### Coverage Gaps
- `src/utils/validation.ts` - 45% (needs tests)
- `src/services/payment.ts` - 62% (edge cases)

### Recommendations
1. Add tests for validation edge cases
2. Fix flaky integration test
3. Improve E2E test stability
```
