# Deepinit Skill

Deep project initialization with best practices.

## When to Use
- Starting new projects
- Setting up development environment
- Adding tooling to existing projects
- Establishing coding standards

## Project Templates

### Full-Stack TypeScript
```
project/
├── apps/
│   ├── web/                 # Next.js frontend
│   └── api/                 # Express/Fastify backend
├── packages/
│   ├── ui/                  # Shared components
│   ├── db/                  # Database schema
│   └── shared/              # Shared utilities
├── .github/
│   └── workflows/           # CI/CD
├── docker-compose.yml
├── turbo.json               # Monorepo config
└── package.json
```

### API Service
```
project/
├── src/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── middleware/
│   └── utils/
├── tests/
├── prisma/
├── Dockerfile
└── package.json
```

### React Application
```
project/
├── src/
│   ├── components/
│   ├── hooks/
│   ├── pages/
│   ├── services/
│   ├── store/
│   ├── styles/
│   └── utils/
├── public/
├── tests/
└── package.json
```

## Setup Components

### TypeScript
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
```

### ESLint
```javascript
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier'
  ],
  rules: {
    // Custom rules
  }
};
```

### Prettier
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

### Git Hooks
```json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged",
      "commit-msg": "commitlint -E HUSKY_GIT_PARAMS"
    }
  },
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"]
  }
}
```

### CI/CD (GitHub Actions)
```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run lint
      - run: npm run test
      - run: npm run build
```

## Usage

```
deepinit: create a new Next.js project with TypeScript, Tailwind, and testing

deepinit: set up a Node.js API with Express, Prisma, and Docker

deepinit: initialize a React Native app with TypeScript
```

## Best Practices Applied

1. **TypeScript** - Strict mode enabled
2. **Linting** - ESLint + Prettier
3. **Testing** - Jest/Vitest configured
4. **Git** - Hooks for quality gates
5. **CI/CD** - Automated pipelines
6. **Docker** - Containerization ready
7. **Documentation** - README template
