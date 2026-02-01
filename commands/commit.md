---
description: Smart conventional commits with context
darwin_version: 1.0.0
darwin_modules:
  input: v3
  research: v3
  structure: v1
  output: v2
  workflow: v2
  validation: v2
---

# Smart Commit

Create a well-crafted conventional commit based on staged changes.

## Process

### 1. Check Status
Run `git status` and `git diff --staged` to understand changes.

### 2. Analyze Changes
- What files were modified?
- What was the nature of the change?
- Is this a single logical change or multiple?

### 3. Determine Commit Type

| Type | When to Use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code restructuring (no behavior change) |
| `style` | Formatting, whitespace, missing semicolons |
| `docs` | Documentation only |
| `test` | Adding or fixing tests |
| `chore` | Build, dependencies, config |
| `perf` | Performance improvement |

### 4. Craft Message

**Format:**
```
type(scope): short description

[optional body with more detail]

[optional footer]
```

**Rules:**
- Subject line: imperative mood, lowercase, no period, max 50 chars
- Scope: component/area affected (optional but helpful)
- Body: wrap at 72 chars, explain "what" and "why"

## Examples

```bash
# Simple feature
feat(camera): add video recording capability

# Bug fix with context
fix(auth): prevent duplicate login requests

Race condition occurred when users double-tapped login button.
Added debounce and disabled state during request.

# Refactor
refactor(store): migrate from Redux to Zustand
```

If changes should be split into multiple commits, suggest which files to unstage.




## Context

Proceed directly with the task. Only search if explicitly needed.


## Output Format

Use clean markdown without decorative elements:
- Standard headers (## ###)
- Simple horizontal rules (---)
- No ASCII art


## Workflow

1. Show what will be done
2. Ask for confirmation
3. Execute only after approval


## Pre-action Checks

Before proceeding, verify:
- [ ] TypeScript compiles
- [ ] No console.logs in production code
- [ ] No `any` types added
- [ ] Follows project conventions

