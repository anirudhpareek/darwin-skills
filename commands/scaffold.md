---
description: Generate boilerplate matching project patterns
darwin_version: 1.0.2
darwin_modules:
  input: v1
  research: v3
  structure: v2
  output: v3
  workflow: v3
  validation: v3
---

# Scaffold Generator

Generate new files matching existing project patterns and conventions.

## Input

**What to scaffold:** $ARGUMENTS

Examples:
- `screen ProfileScreen` - New screen
- `component Avatar` - New component
- `hook useDebounce` - New hook

## Process

1. Detect project type from current directory
2. Analyze existing similar files for patterns
3. Generate matching boilerplate
4. Create file and update barrel exports if applicable

## Templates

Generate code that matches the project's:
- Naming conventions
- File structure
- Import patterns
- Type definitions


## Input

**Task:** $ARGUMENTS

If no arguments provided, ask the user what they want to accomplish.


## Context

Proceed directly with the task. Only search if explicitly needed.


## Output Format

Keep output extremely concise:
- No explanatory text
- Data only, no decoration
- Under 30 lines total


## Workflow

Execute the action immediately. Only pause if:
- Destructive operation detected
- Ambiguity in requirements



