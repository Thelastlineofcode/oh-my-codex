# Playwright Skill

Browser automation and E2E testing with Playwright.

## When to Use
- Writing E2E tests
- Browser automation scripts
- Web scraping
- Visual regression testing
- Cross-browser testing

## When NOT to Use
- Unit tests (use Jest/Vitest)
- API-only tests (use direct HTTP)
- Simple DOM testing (use Testing Library)

## Setup

```bash
# Install
npm init playwright@latest

# Or add to existing project
npm install -D @playwright/test
npx playwright install
```

## Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should do something', async ({ page }) => {
    // Arrange
    await page.fill('[data-testid="email"]', 'user@example.com');
    
    // Act
    await page.click('button[type="submit"]');
    
    // Assert
    await expect(page.locator('.success')).toBeVisible();
  });
});
```

## Common Patterns

### Locators (Preferred Order)
```typescript
// 1. Role (best for accessibility)
page.getByRole('button', { name: 'Submit' })

// 2. Test ID (explicit)
page.getByTestId('submit-button')

// 3. Text
page.getByText('Submit')

// 4. Label
page.getByLabel('Email')

// 5. CSS (last resort)
page.locator('.submit-btn')
```

### Waiting
```typescript
// Auto-wait (built-in)
await page.click('button'); // waits for button to be actionable

// Explicit wait
await page.waitForSelector('.loaded');
await page.waitForLoadState('networkidle');
await page.waitForResponse(resp => resp.url().includes('/api/data'));

// Wait for condition
await expect(page.locator('.item')).toHaveCount(5);
```

### Forms
```typescript
// Fill form
await page.fill('#email', 'user@example.com');
await page.fill('#password', 'secret');

// Select dropdown
await page.selectOption('#country', 'US');

// Checkbox/Radio
await page.check('#agree');
await page.uncheck('#newsletter');

// File upload
await page.setInputFiles('#avatar', 'path/to/file.png');
```

### Assertions
```typescript
// Visibility
await expect(locator).toBeVisible();
await expect(locator).toBeHidden();

// Text
await expect(locator).toHaveText('Hello');
await expect(locator).toContainText('Hello');

// Attributes
await expect(locator).toHaveAttribute('href', '/home');
await expect(locator).toHaveClass(/active/);

// Count
await expect(locator).toHaveCount(5);

// URL
await expect(page).toHaveURL(/dashboard/);
```

### Page Object Model
```typescript
// pages/login.page.ts
export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.page.fill('#email', email);
    await this.page.fill('#password', password);
    await this.page.click('button[type="submit"]');
  }
}

// tests/login.spec.ts
test('login flow', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password');
  await expect(page).toHaveURL('/dashboard');
});
```

## Configuration

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  retries: process.env.CI ? 2 : 0,
  
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },

  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
    { name: 'firefox', use: { browserName: 'firefox' } },
    { name: 'webkit', use: { browserName: 'webkit' } },
  ],
});
```

## Running Tests

```bash
# Run all
npx playwright test

# Run specific file
npx playwright test login.spec.ts

# Run with UI
npx playwright test --ui

# Debug mode
npx playwright test --debug

# Show report
npx playwright show-report
```
