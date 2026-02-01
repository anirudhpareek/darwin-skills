---
description: Generate structured implementation plans
darwin_version: 1.0.0
darwin_modules:
  input: v1
  research: v2
  structure: v1
  output: v1
  workflow: v1
  validation: v3
---

# Implementation Plan Generator

Generate a detailed implementation plan for the given feature or task.

## Analysis Steps

1. **Understand the Request**
   - What is being asked?
   - What is the expected outcome?
   - What are the constraints?

2. **Explore the Codebase**
   - Search for related files and patterns
   - Understand existing conventions
   - Identify dependencies

3. **Generate Plan**

## Plan Template

```
═══════════════════════════════════════════════════
IMPLEMENTATION PLAN: [Feature Name]
═══════════════════════════════════════════════════

## 1. Requirements Analysis

**Goal:** [1-2 sentence summary]

**User Stories:**
- As a user, I want to...

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

---

## 2. Files to Modify/Create

| Action | File | Purpose |
|--------|------|---------|
| CREATE | path/to/file.tsx | Description |
| MODIFY | path/to/existing.tsx | Description |

---

## 3. Implementation Steps

### Step 1: [Name]
**Files:** `file1.tsx`, `file2.tsx`
**Details:**
- Specific change 1
- Specific change 2

---

## 4. Testing Strategy

**Manual Testing:**
- [ ] Test case 1

---

## 5. Risks & Unknowns

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Risk 1 | Low/Med/High | How to handle |

═══════════════════════════════════════════════════
```

## Guidelines

1. Be specific about file paths and changes
2. Consider edge cases and error handling
3. Keep scope focused - avoid feature creep


## Input

**Task:** $ARGUMENTS

If no arguments provided, ask the user what they want to accomplish.


## Research Steps

1. **Read project conventions**
   - Read CLAUDE.md for project-specific patterns
   - Note any "Do NOT" sections
   - Understand the preferred style

2. **Search codebase**
   - Search for similar implementations
   - Follow conventions from CLAUDE.md
   - Identify dependencies


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



