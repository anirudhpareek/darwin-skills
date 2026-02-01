---
description: Loop - run build, fix errors, repeat until clean
---

# Build Fix Loop

Automatically run the build, parse errors, and fix them in a loop until the build passes.

## Process

### 1. Detect Build Command
Based on project:
- React Native/Expo: `npx tsc --noEmit`
- Next.js: `npm run build` or `npx tsc --noEmit`
- Generic: `npm run build`

### 2. Run Build Loop

```
ITERATION 1
═══════════════════════════════════════════════════
Running: npx tsc --noEmit

[Output]

Found X errors

Fixing:
  1. file.tsx:42 - TS2339: Property 'foo' does not exist
     Fix: [description of fix]

  2. file.tsx:55 - TS2345: Argument of type...
     Fix: [description of fix]

═══════════════════════════════════════════════════
ITERATION 2
...
```

### 3. Error Categories

| Error Type | Strategy |
|------------|----------|
| Missing import | Add import statement |
| Type mismatch | Fix type or add assertion |
| Missing property | Add to interface or fix typo |
| Unused variable | Remove or prefix with _ |
| Missing return | Add return statement |

### 4. Loop Rules

- Maximum 10 iterations (prevent infinite loops)
- If same error persists 3 times, stop and ask for help
- After each fix, run build again to verify
- Don't make changes that could break runtime behavior

---

## Output Format

```
═══════════════════════════════════════════════════
BUILD FIX LOOP
═══════════════════════════════════════════════════

Starting build check...

ITERATION 1
───────────────────
Errors found: 5

[Fix 1] src/components/Button.tsx:23
  Error: TS2339 - Property 'onPress' does not exist on type
  Fix: Added 'onPress' to ButtonProps interface

[Fix 2] src/screens/HomeScreen.tsx:45
  Error: TS2345 - Argument type mismatch
  Fix: Updated function parameter type

Building again...

ITERATION 2
───────────────────
Errors found: 1

[Fix 3] src/store/useAppStore.ts:12
  Error: TS2322 - Type 'string' is not assignable to 'number'
  Fix: Changed type annotation

Building again...

═══════════════════════════════════════════════════
BUILD SUCCESSFUL
═══════════════════════════════════════════════════

Fixed 3 errors in 2 iterations.

Changes made:
- src/components/Button.tsx (1 fix)
- src/screens/HomeScreen.tsx (1 fix)
- src/store/useAppStore.ts (1 fix)
```

---

## Safety

- Only fix TypeScript errors, not warnings
- Preserve existing behavior
- If uncertain about a fix, ask first
- Show diff before applying risky changes

---

## Commands

```bash
# Type check only (faster)
npx tsc --noEmit

# Full build
npm run build

# With watch (for development)
npx tsc --noEmit --watch
```

After success, offer to run linting or tests next.
