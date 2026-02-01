---
description: Review implementation plans with staff-engineer perspective
---

# Plan Review (Staff Engineer Perspective)

Review the provided implementation plan as a senior/staff engineer would.

## Input

**Plan to Review:** $ARGUMENTS

If no plan provided, ask user to paste the plan or reference a file.

---

## Review Checklist

### 1. Completeness
- [ ] Are all requirements addressed?
- [ ] Are edge cases considered?
- [ ] Is error handling planned?
- [ ] Are all affected files identified?

### 2. Feasibility
- [ ] Is the scope realistic?
- [ ] Are there hidden complexities?
- [ ] Do the proposed changes fit existing patterns?
- [ ] Are dependencies correctly identified?

### 3. Architecture
- [ ] Does it follow project conventions?
- [ ] Is the separation of concerns correct?
- [ ] Will this be maintainable?
- [ ] Does it introduce tech debt?

### 4. Risk Assessment
- [ ] What could go wrong?
- [ ] What's the blast radius if it fails?
- [ ] Are there rollback considerations?
- [ ] Performance implications?

### 5. Missing Elements
- [ ] Migration needs?
- [ ] Documentation updates?
- [ ] Analytics/logging?
- [ ] Accessibility considerations?

---

## Output Format

```
═══════════════════════════════════════════════════
PLAN REVIEW
═══════════════════════════════════════════════════

## Overall Assessment
[APPROVE / NEEDS CHANGES / REJECT]

**Summary:** [1-2 sentences]

---

## Strengths
- Good aspect 1
- Good aspect 2

---

## Concerns

### Critical (Must Address)
1. **Issue:** Description
   **Fix:** Suggested resolution

### Important (Should Address)
1. **Issue:** Description
   **Fix:** Suggested resolution

### Minor (Nice to Have)
1. **Issue:** Description
   **Fix:** Suggested resolution

---

## Missing from Plan
- Item 1
- Item 2

---

## Questions for Author
1. Question 1?
2. Question 2?

---

## Revised Recommendations

[If changes needed, provide specific modifications]

═══════════════════════════════════════════════════
```

---

## Review Mindset

Think like a staff engineer:
- "What will break?"
- "What's the simplest solution?"
- "Will we regret this in 6 months?"
- "Is this solving the right problem?"
- "What are we not considering?"

Be constructive but direct. Identify problems AND suggest solutions.
