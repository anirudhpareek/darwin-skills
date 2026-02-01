#!/usr/bin/env python3
"""
Darwin Skill Compiler
Compiles skill definitions (YAML) into executable skills (Markdown)
Usage: python compile.py [skill_name] or python compile.py --all
"""

import os
import sys
import yaml
from datetime import datetime
from pathlib import Path

DARWIN_DIR = Path.home() / ".claude" / "darwin"
MODULES_FILE = DARWIN_DIR / "modules" / "registry.yaml"
SKILLS_DIR = DARWIN_DIR / "skills"
OUTPUT_DIR = Path.home() / ".claude" / "commands"


def load_yaml(path):
    """Load YAML file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def save_yaml(path, data):
    """Save YAML file."""
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def get_module_prompt(registry, module_type, version):
    """Get module prompt by type and version."""
    modules = registry.get('modules', {})
    module = modules.get(module_type, {})
    variant = module.get(version, {})
    return variant.get('prompt', '')


def compile_skill(skill_name, registry):
    """Compile a single skill from its definition."""
    skill_file = SKILLS_DIR / f"{skill_name}.yaml"
    output_file = OUTPUT_DIR / f"{skill_name}.md"

    if not skill_file.exists():
        print(f"Error: Skill definition not found: {skill_file}")
        return False

    print(f"Compiling: {skill_name}")

    # Load skill definition
    skill = load_yaml(skill_file)

    # Get metadata
    description = skill.get('description', '')
    version = skill.get('version', '1.0.0')

    # Get module versions
    modules = skill.get('modules', {})
    input_ver = modules.get('input', 'v1')
    research_ver = modules.get('research', 'v1')
    structure_ver = modules.get('structure', 'v1')
    output_ver = modules.get('output', 'v1')
    workflow_ver = modules.get('workflow', 'v1')
    validation_ver = modules.get('validation', 'v3')

    # Get module prompts
    input_prompt = get_module_prompt(registry, 'input', input_ver)
    research_prompt = get_module_prompt(registry, 'research', research_ver)
    output_prompt = get_module_prompt(registry, 'output', output_ver)
    workflow_prompt = get_module_prompt(registry, 'workflow', workflow_ver)
    validation_prompt = get_module_prompt(registry, 'validation', validation_ver)

    # Get core prompt
    core_prompt = skill.get('core_prompt', '')

    # Assemble the skill
    assembled = f"""---
description: {description}
darwin_version: {version}
darwin_modules:
  input: {input_ver}
  research: {research_ver}
  structure: {structure_ver}
  output: {output_ver}
  workflow: {workflow_ver}
  validation: {validation_ver}
---

{core_prompt}

{input_prompt}

{research_prompt}

{output_prompt}

{workflow_prompt}

{validation_prompt}
"""

    # Write output
    with open(output_file, 'w') as f:
        f.write(assembled)

    # Update last_compiled in skill definition
    skill['last_compiled'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    save_yaml(skill_file, skill)

    print(f"  → {output_file}")
    print(f"  Modules: input={input_ver} research={research_ver} structure={structure_ver} output={output_ver} workflow={workflow_ver} validation={validation_ver}")

    return True


def main():
    # Check if registry exists
    if not MODULES_FILE.exists():
        print(f"Error: Module registry not found: {MODULES_FILE}")
        sys.exit(1)

    # Load registry
    registry = load_yaml(MODULES_FILE)

    if len(sys.argv) < 2:
        print("Usage: compile.py [skill_name] or compile.py --all")
        print("")
        print("Available skills:")
        for skill_file in SKILLS_DIR.glob("*.yaml"):
            print(f"  - {skill_file.stem}")
        sys.exit(0)

    if sys.argv[1] == "--all":
        print("═══════════════════════════════════════════════════")
        print("DARWIN SKILL COMPILER - All Skills")
        print("═══════════════════════════════════════════════════")
        print("")

        for skill_file in SKILLS_DIR.glob("*.yaml"):
            compile_skill(skill_file.stem, registry)
            print("")

        print("═══════════════════════════════════════════════════")
        print("Compilation complete")
        print("═══════════════════════════════════════════════════")
    else:
        compile_skill(sys.argv[1], registry)


if __name__ == "__main__":
    main()
