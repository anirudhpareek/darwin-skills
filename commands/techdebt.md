---
description: Find code smells, duplicates, and TODOs
darwin_version: 1.0.2
darwin_modules:
  input: v2
  research: v1
  structure: v1
  output: v1
  workflow: v1
  validation: v3
---

# Tech Debt Analysis

Analyze the codebase for technical debt, code smells, and areas for improvement.

## Analysis Categories

### 1. TODOs & FIXMEs
Search for and catalog all TODO, FIXME, HACK, XXX comments.

### 2. Code Duplication
Identify similar code patterns that could be abstracted.

### 3. Code Smells

| Smell | What to Look For |
|-------|------------------|
| Long functions | Functions > 50 lines |
| Large files | Files > 300 lines |
| Deep nesting | > 3 levels of indentation |
| Magic numbers | Unexplained numeric literals |
| Any types | TypeScript `any` usage |
| Console logs | Leftover debugging |

### 4. Pattern Violations
Deviations from project conventions (per CLAUDE.md)

## Output Template

```
═══════════════════════════════════════════════════
TECH DEBT REPORT: [Project/Path]
═══════════════════════════════════════════════════

SUMMARY
───────────────────────────────────────────────────
- TODOs/FIXMEs: X items
- Code Smells: X items
- Duplications: X instances

DETAILS
───────────────────────────────────────────────────
[Categorized findings with file:line references]

QUICK WINS
───────────────────────────────────────────────────
Items that can be fixed in < 5 minutes

═══════════════════════════════════════════════════
```


## Input

**Scope:** $ARGUMENTS

If no arguments provided, analyze the current project directory.


## Research Steps

1. **Search for patterns**
   - Use Grep to find related implementations
   - Look for similar naming conventions
   - Identify test files if they exist

2. **Read relevant files**
   - Read files that match the search results
   - Understand the existing patterns
   - Note any dependencies


## Output Format

Use ASCII dividers for sections:
```
═══════════════════════════════════════════════════
TITLE: [Name]
═══════════════════════════════════════════════════

SECTION
───────────────────────────────────────────────────
Content here...

═══════════════════════════════════════════════════
```


## Next Steps

After generating output, offer to:
- Execute the plan immediately
- Export for review
- Modify based on feedback



