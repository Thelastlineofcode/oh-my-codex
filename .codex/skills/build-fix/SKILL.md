# Build Fix Skill

Fix build errors and compilation issues.

## When to Use
- Build failures
- Compilation errors
- TypeScript errors
- Lint errors
- Dependency issues

## Error Categories

### TypeScript Errors
```typescript
// TS2322: Type mismatch
const x: string = 123; // Error
const x: string = "123"; // Fix

// TS2339: Property doesn't exist
obj.unknownProp; // Error
obj.knownProp; // Fix (or add to type)

// TS2345: Argument type mismatch
fn(wrongType); // Error
fn(correctType); // Fix

// TS7006: Implicit any
function fn(x) {} // Error
function fn(x: string) {} // Fix
```

### Import Errors
```typescript
// Module not found
import { x } from 'nonexistent';
// Fix: Install package or correct path

// Named export doesn't exist
import { wrong } from 'module';
// Fix: Check actual exports

// Default vs named
import wrong from 'module'; // Has named exports
import { correct } from 'module';
```

### Lint Errors
```javascript
// ESLint: no-unused-vars
const unused = 1; // Error
// Fix: Remove or use the variable

// ESLint: no-console
console.log('debug'); // Error
// Fix: Remove or configure rule

// Prettier: formatting
const x={a:1}; // Error
const x = { a: 1 }; // Fix
```

## Fix Strategy

### 1. Identify
```bash
npm run build 2>&1 | head -50
npm run typecheck
npm run lint
```

### 2. Categorize
```
- Type errors → Fix types
- Import errors → Fix imports
- Lint errors → Fix style
- Runtime errors → Fix logic
```

### 3. Fix Order
```
1. Dependency errors (install packages)
2. Import errors (fix paths)
3. Type errors (fix types)
4. Lint errors (fix style)
```

### 4. Verify
```bash
npm run build
npm run test
```

## Common Fixes

### Missing Type
```typescript
// Before
const data = fetchData();

// After
interface Data { id: string; name: string; }
const data: Data = fetchData();
```

### Null Check
```typescript
// Before
user.name.toUpperCase();

// After
user?.name?.toUpperCase();
// or
if (user && user.name) {
  user.name.toUpperCase();
}
```

### Async/Await
```typescript
// Before
const data = fetchData(); // Promise, not data

// After
const data = await fetchData();
```

## Usage

```
build-fix: fix all TypeScript errors

build-fix: resolve the compilation failures

build-fix: fix lint errors in src/
```

## Automation

```bash
# Auto-fix lint
npm run lint -- --fix

# Auto-fix prettier
npm run format

# Type check
npm run typecheck
```
