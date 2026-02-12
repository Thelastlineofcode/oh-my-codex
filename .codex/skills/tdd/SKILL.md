# TDD Skill

Test-Driven Development workflow.

## When to Use
- Building new features with clear requirements
- Refactoring with safety net
- Bug fixes (reproduce first, then fix)
- When code correctness is critical

## When NOT to Use
- Exploratory prototyping
- UI/visual development
- One-off scripts

## TDD Cycle

```
   ┌─────────────────┐
   │   RED           │
   │   Write a       │
   │   failing test  │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │   GREEN         │
   │   Make it       │
   │   pass          │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │   REFACTOR      │
   │   Clean up      │
   │   the code      │
   └────────┬────────┘
            │
            └──────────→ (repeat)
```

## Workflow

### 1. RED - Write Failing Test

```typescript
// Write the test FIRST
test('should calculate total with tax', () => {
  const cart = new Cart();
  cart.add({ price: 100 });
  expect(cart.totalWithTax(0.1)).toBe(110);
});
```

Run test → Should FAIL (function doesn't exist yet)

### 2. GREEN - Minimal Implementation

```typescript
// Write JUST enough to pass
class Cart {
  items = [];
  add(item) { this.items.push(item); }
  totalWithTax(rate) {
    const subtotal = this.items.reduce((sum, i) => sum + i.price, 0);
    return subtotal * (1 + rate);
  }
}
```

Run test → Should PASS

### 3. REFACTOR - Improve

```typescript
// Now clean up
class Cart {
  private items: CartItem[] = [];
  
  add(item: CartItem): void {
    this.items.push(item);
  }
  
  get subtotal(): number {
    return this.items.reduce((sum, item) => sum + item.price, 0);
  }
  
  totalWithTax(taxRate: number): number {
    return this.subtotal * (1 + taxRate);
  }
}
```

Run test → Should still PASS

## Test Structure

```typescript
describe('Feature', () => {
  // Setup
  beforeEach(() => { /* reset state */ });
  
  // Happy path
  test('should work with valid input', () => {});
  
  // Edge cases
  test('should handle empty input', () => {});
  test('should handle null', () => {});
  
  // Error cases
  test('should throw on invalid input', () => {});
});
```

## Usage

```
tdd: implement a shopping cart with discount codes

tdd: build a rate limiter with sliding window

tdd: create a date range validator
```

## Best Practices

1. **One assertion per test** (usually)
2. **Descriptive test names** - "should X when Y"
3. **Arrange-Act-Assert** pattern
4. **Test behavior, not implementation**
5. **Keep tests fast**
