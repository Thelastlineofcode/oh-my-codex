# Eco Skill

Token-efficient mode for simple tasks.

## When to Use
- Simple, well-understood tasks
- Quick fixes and small changes
- When user values speed over explanation
- Routine operations

## When NOT to Use
- Complex architectural decisions
- When user needs to understand the changes
- Debugging (need verbose output)
- Learning/teaching scenarios

## Principles

```
1. MINIMAL CONFIRMATION
   - Don't ask "shall I proceed?" for obvious tasks
   - Just do it, show the result

2. TERSE OUTPUT
   - Skip explanations unless asked
   - Show diff, not description
   - One-line summaries

3. FAST ROUTING
   - Use simplest approach
   - Avoid over-engineering
   - Skip optional validations for trivial changes

4. BATCH WHEN POSSIBLE
   - Combine related small changes
   - Single commit for related fixes
```

## Response Format

```
✓ {what was done}
```

That's it. No preamble, no follow-up questions unless truly needed.

## Examples

**User:** "eco: add .env to gitignore"
**Response:** 
```
✓ Added .env to .gitignore
```

**User:** "eco: fix the typo in line 42"
**Response:**
```
✓ Fixed "recieve" → "receive" in src/utils.ts:42
```

## Anti-patterns

❌ "I'll help you add .env to your .gitignore file. Let me first check if the file exists..."

❌ "Done! I've successfully added .env to your .gitignore. Is there anything else you'd like me to help with?"

✅ "✓ Added .env to .gitignore"
