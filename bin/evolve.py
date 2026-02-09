#!/usr/bin/env python3
"""
Darwin Evolution Engine
Automatically evolves skills based on fitness metrics.

Operations:
- EVALUATE: Score all skills
- MUTATE: Try different module versions for underperformers
- ABSORB: Copy patterns from top performers
- PRUNE: Mark unused skills for deprecation
- CHANGELOG: Record evolution history

Usage:
  python evolve.py status      # Show current fitness + recommendations
  python evolve.py suggest     # Generate evolution suggestions
  python evolve.py apply       # Apply suggested mutations
  python evolve.py cycle       # Full evolution cycle
"""

import os
import sys
import json
import yaml
import random
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DARWIN_DIR = Path.home() / ".claude" / "darwin"
MODULES_FILE = DARWIN_DIR / "modules" / "registry.yaml"
SKILLS_DIR = DARWIN_DIR / "skills"
CHANGELOGS_DIR = DARWIN_DIR / "changelogs"
EVALUATIONS_DIR = DARWIN_DIR / "evaluations"

# Fitness thresholds
THRESHOLDS = {
    "top_performer": 0.70,
    "healthy": 0.50,
    "underperforming": 0.35,
    "failing": 0.20
}


def load_yaml(path: Path) -> dict:
    """Load YAML file."""
    if not path.exists():
        return {}
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}


def save_yaml(path: Path, data: dict):
    """Save YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def run_evaluate() -> dict:
    """Run evaluate.sh and return results."""
    result = subprocess.run(
        [str(DARWIN_DIR / "bin" / "evaluate.sh")],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return {"error": result.stderr, "skills": []}
    return json.loads(result.stdout)


def get_module_variants(registry: dict, module_type: str) -> List[str]:
    """Get all variants for a module type."""
    modules = registry.get('modules', {})
    module = modules.get(module_type, {})
    return list(module.keys())


def classify_skill(fitness: float) -> str:
    """Classify skill by fitness score."""
    if fitness >= THRESHOLDS["top_performer"]:
        return "top_performer"
    elif fitness >= THRESHOLDS["healthy"]:
        return "healthy"
    elif fitness >= THRESHOLDS["underperforming"]:
        return "underperforming"
    else:
        return "failing"


def get_skill_fitness(evaluation: dict, skill_name: str) -> Optional[float]:
    """Get fitness score for a specific skill from evaluation results."""
    for skill in evaluation.get('skills', []):
        if skill.get('skill') == skill_name:
            return skill.get('fitness')
    return None


def get_recently_tried_variants(skill_def: dict) -> set:
    """Extract variants that were recently tried to prevent oscillation."""
    recent_history = skill_def.get('fitness_history', [])[-10:]
    recently_tried = set()
    for h in recent_history:
        mutation_str = h.get('mutation', '')
        if '→' in mutation_str:
            # Extract "module: old → new" format
            parts = mutation_str.split('→')
            if len(parts) == 2:
                # Get the "to" version (after arrow)
                to_version = parts[1].strip()
                # Get module name from "module: old" part
                module_parts = parts[0].split(':')
                if len(module_parts) == 2:
                    module_name = module_parts[0].strip()
                    recently_tried.add(f"{module_name}:{to_version}")
    return recently_tried


def suggest_mutations(skill_name: str, skill_def: dict, fitness: float,
                      registry: dict, top_performers: List[dict]) -> List[dict]:
    """Suggest module mutations for a skill."""
    suggestions = []
    current_modules = skill_def.get('modules', {})
    classification = classify_skill(fitness)

    # Track recently tried variants to prevent oscillation
    recently_tried = get_recently_tried_variants(skill_def)

    if classification in ["healthy", "top_performer"]:
        return []  # Don't mutate successful skills

    # Strategy 1: Copy modules from top performers
    for top in top_performers:
        top_skill_file = SKILLS_DIR / f"{top['skill']}.yaml"
        if top_skill_file.exists():
            top_def = load_yaml(top_skill_file)
            top_modules = top_def.get('modules', {})

            for module_type, top_version in top_modules.items():
                variant_key = f"{module_type}:{top_version}"
                # Skip if this variant was recently tried (prevents oscillation)
                if variant_key in recently_tried:
                    continue
                if current_modules.get(module_type) != top_version:
                    suggestions.append({
                        "type": "absorb",
                        "skill": skill_name,
                        "module": module_type,
                        "from_version": current_modules.get(module_type, "unknown"),
                        "to_version": top_version,
                        "reason": f"Absorb from top performer /{top['skill']} (fitness: {top['fitness']:.2f})"
                    })

    # Strategy 2: Try alternative module versions
    for module_type, current_version in current_modules.items():
        variants = get_module_variants(registry, module_type)
        for variant in variants:
            variant_key = f"{module_type}:{variant}"
            # Skip if recently tried (prevents oscillation)
            if variant_key in recently_tried:
                continue
            if variant != current_version:
                # Only suggest if not already suggested via absorption
                already_suggested = any(
                    s['module'] == module_type and s['to_version'] == variant
                    for s in suggestions
                )
                if not already_suggested:
                    suggestions.append({
                        "type": "mutate",
                        "skill": skill_name,
                        "module": module_type,
                        "from_version": current_version,
                        "to_version": variant,
                        "reason": f"Try alternative variant (not recently tried)"
                    })

    # If all variants were recently tried, suggest waiting
    if not suggestions and classification in ["underperforming", "failing"]:
        # Could add a "cooldown" suggestion here in future
        pass

    return suggestions


def apply_mutation(skill_name: str, module_type: str, new_version: str) -> bool:
    """Apply a single mutation to a skill."""
    skill_file = SKILLS_DIR / f"{skill_name}.yaml"
    if not skill_file.exists():
        print(f"  Error: Skill file not found: {skill_file}")
        return False

    skill_def = load_yaml(skill_file)
    old_version = skill_def.get('modules', {}).get(module_type, 'unknown')

    # Update module version
    if 'modules' not in skill_def:
        skill_def['modules'] = {}
    skill_def['modules'][module_type] = new_version

    # Bump version
    version = skill_def.get('version', '1.0.0')
    parts = version.split('.')
    parts[-1] = str(int(parts[-1]) + 1)
    skill_def['version'] = '.'.join(parts)

    # Add to fitness history
    if 'fitness_history' not in skill_def:
        skill_def['fitness_history'] = []
    skill_def['fitness_history'].append({
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mutation": f"{module_type}: {old_version} → {new_version}"
    })

    save_yaml(skill_file, skill_def)
    return True


def recompile_skill(skill_name: str) -> bool:
    """Recompile a skill after mutation."""
    result = subprocess.run(
        ["python3", str(DARWIN_DIR / "bin" / "compile.py"), skill_name],
        capture_output=True, text=True
    )
    return result.returncode == 0


def write_changelog(skill_name: str, mutations: List[dict], old_fitness: float, new_fitness: Optional[float] = None):
    """Write changelog entry for skill evolution."""
    changelog_file = CHANGELOGS_DIR / f"{skill_name}.md"
    CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing changelog
    if changelog_file.exists():
        with open(changelog_file, 'r') as f:
            content = f.read()
    else:
        content = f"# /{skill_name} Evolution Changelog\n\n"

    # Get current version
    skill_file = SKILLS_DIR / f"{skill_name}.yaml"
    skill_def = load_yaml(skill_file) if skill_file.exists() else {}
    version = skill_def.get('version', '?.?.?')

    # Build entry
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n## v{version} ({timestamp})\n\n"
    entry += f"**Fitness:** {old_fitness:.2f}"
    if new_fitness is not None:
        delta = new_fitness - old_fitness
        entry += f" → {new_fitness:.2f} ({'+' if delta >= 0 else ''}{delta:.2f})"
    entry += "\n\n"

    entry += "**Mutations:**\n"
    for m in mutations:
        entry += f"- `{m['module']}`: {m['from_version']} → {m['to_version']} ({m['type']})\n"
        entry += f"  - Reason: {m['reason']}\n"

    entry += "\n---\n"

    # Prepend entry (newest first)
    header_end = content.find("\n## ")
    if header_end == -1:
        content = content + entry
    else:
        content = content[:header_end] + entry + content[header_end:]

    with open(changelog_file, 'w') as f:
        f.write(content)


def print_status(evaluation: dict):
    """Print current fitness status."""
    print("═══════════════════════════════════════════════════")
    print("DARWIN EVOLUTION STATUS")
    print("═══════════════════════════════════════════════════")
    print()

    total = evaluation.get('total_invocations', 0)
    print(f"DATA: {total} skill invocations │ Period: last 7 days")
    print()

    skills = evaluation.get('skills', [])
    if not skills:
        print("No skills to evaluate.")
        return

    print("SKILL FITNESS")
    print("───────────────────────────────────────────────────")

    for i, skill in enumerate(skills, 1):
        name = skill['skill']
        fitness = skill['fitness']
        invocations = skill['invocations']
        classification = classify_skill(fitness)

        # Build bar
        bar_filled = int(fitness * 10)
        bar = "█" * bar_filled + "░" * (10 - bar_filled)

        # Status indicator
        if classification == "top_performer":
            status = "★"
        elif classification == "healthy":
            status = "✓"
        elif classification == "underperforming":
            status = "↓"
        else:
            status = "✗"

        print(f" {i:2}. /{name:12} {bar}  {fitness:.2f}  [{invocations:2} uses] {status}")

    print()
    print("LEGEND: ★ top performer  ✓ healthy  ↓ underperforming  ✗ failing")
    print("═══════════════════════════════════════════════════")


def cmd_status():
    """Show fitness status."""
    evaluation = run_evaluate()
    if "error" in evaluation:
        print(f"Error: {evaluation['error']}")
        return
    print_status(evaluation)


def cmd_suggest():
    """Generate evolution suggestions."""
    evaluation = run_evaluate()
    if "error" in evaluation:
        print(f"Error: {evaluation['error']}")
        return

    registry = load_yaml(MODULES_FILE)
    skills = evaluation.get('skills', [])

    # Identify top performers
    top_performers = [s for s in skills if classify_skill(s['fitness']) == "top_performer"]

    print("═══════════════════════════════════════════════════")
    print("DARWIN EVOLUTION SUGGESTIONS")
    print("═══════════════════════════════════════════════════")
    print()

    all_suggestions = []

    for skill_data in skills:
        skill_name = skill_data['skill']
        fitness = skill_data['fitness']
        classification = classify_skill(fitness)

        if classification in ["underperforming", "failing"]:
            skill_file = SKILLS_DIR / f"{skill_name}.yaml"
            if not skill_file.exists():
                continue

            skill_def = load_yaml(skill_file)
            suggestions = suggest_mutations(
                skill_name, skill_def, fitness, registry, top_performers
            )

            if suggestions:
                print(f"/{skill_name} (fitness: {fitness:.2f}, {classification})")
                print("───────────────────────────────────────────────────")

                # Show top 3 suggestions
                for s in suggestions[:3]:
                    print(f"  [{s['type'].upper()}] {s['module']}: {s['from_version']} → {s['to_version']}")
                    print(f"           {s['reason']}")

                all_suggestions.extend(suggestions[:3])
                print()

    if not all_suggestions:
        print("No mutations needed. All skills are healthy or top performers.")
    else:
        print(f"Total suggestions: {len(all_suggestions)}")
        print()
        print("Run 'python evolve.py apply' to apply top suggestion per skill.")

    print("═══════════════════════════════════════════════════")


def cmd_apply():
    """Apply evolution suggestions."""
    evaluation = run_evaluate()
    if "error" in evaluation:
        print(f"Error: {evaluation['error']}")
        return

    registry = load_yaml(MODULES_FILE)
    skills = evaluation.get('skills', [])
    top_performers = [s for s in skills if classify_skill(s['fitness']) == "top_performer"]

    print("═══════════════════════════════════════════════════")
    print("DARWIN EVOLUTION - APPLYING MUTATIONS")
    print("═══════════════════════════════════════════════════")
    print()

    mutations_applied = []

    for skill_data in skills:
        skill_name = skill_data['skill']
        fitness = skill_data['fitness']
        classification = classify_skill(fitness)

        if classification not in ["underperforming", "failing"]:
            continue

        skill_file = SKILLS_DIR / f"{skill_name}.yaml"
        if not skill_file.exists():
            continue

        skill_def = load_yaml(skill_file)
        suggestions = suggest_mutations(
            skill_name, skill_def, fitness, registry, top_performers
        )

        if not suggestions:
            continue

        # Apply top suggestion (prefer absorb over mutate)
        absorb_suggestions = [s for s in suggestions if s['type'] == 'absorb']
        suggestion = absorb_suggestions[0] if absorb_suggestions else suggestions[0]

        print(f"Evolving /{skill_name}...")
        print(f"  {suggestion['module']}: {suggestion['from_version']} → {suggestion['to_version']}")
        print(f"  Reason: {suggestion['reason']}")

        # Apply mutation
        if apply_mutation(skill_name, suggestion['module'], suggestion['to_version']):
            # Recompile skill
            if recompile_skill(skill_name):
                print(f"  ✓ Mutation applied and recompiled")

                # Post-mutation fitness verification
                print(f"  ⏳ Verifying fitness change...")
                new_evaluation = run_evaluate()
                new_fitness = get_skill_fitness(new_evaluation, skill_name)

                if new_fitness is not None:
                    delta = new_fitness - fitness
                    if delta > 0:
                        print(f"  ✓ Fitness improved: {fitness:.2f} → {new_fitness:.2f} (+{delta:.2f})")
                    elif delta < 0:
                        print(f"  ⚠ Fitness dropped: {fitness:.2f} → {new_fitness:.2f} ({delta:.2f})")
                        print(f"    Consider: python evolve.py rollback {skill_name}")
                    else:
                        print(f"  → Fitness unchanged: {fitness:.2f}")
                else:
                    new_fitness = fitness  # Use old if can't evaluate
                    print(f"  ⚠ Could not verify fitness (using baseline)")

                mutations_applied.append({
                    "skill": skill_name,
                    "old_fitness": fitness,
                    "new_fitness": new_fitness,
                    **suggestion
                })

                # Write changelog with new fitness
                write_changelog(skill_name, [suggestion], fitness, new_fitness)
            else:
                print(f"  ✗ Recompilation failed")
        else:
            print(f"  ✗ Mutation failed")

        print()

    if mutations_applied:
        print("───────────────────────────────────────────────────")
        print(f"Applied {len(mutations_applied)} mutation(s)")
        print("Changelogs updated in ~/.claude/darwin/changelogs/")
    else:
        print("No mutations applied.")

    print("═══════════════════════════════════════════════════")


def cmd_cycle():
    """Run full evolution cycle."""
    print("═══════════════════════════════════════════════════")
    print("DARWIN EVOLUTION CYCLE")
    print("═══════════════════════════════════════════════════")
    print()

    # Step 1: Evaluate
    print("Step 1: EVALUATE")
    print("───────────────────────────────────────────────────")
    evaluation = run_evaluate()
    if "error" in evaluation:
        print(f"Error: {evaluation['error']}")
        return

    skills = evaluation.get('skills', [])
    print(f"Evaluated {len(skills)} skills")

    top = [s for s in skills if classify_skill(s['fitness']) == "top_performer"]
    healthy = [s for s in skills if classify_skill(s['fitness']) == "healthy"]
    under = [s for s in skills if classify_skill(s['fitness']) == "underperforming"]
    failing = [s for s in skills if classify_skill(s['fitness']) == "failing"]

    print(f"  Top performers: {len(top)}")
    print(f"  Healthy: {len(healthy)}")
    print(f"  Underperforming: {len(under)}")
    print(f"  Failing: {len(failing)}")
    print()

    # Step 2: Save snapshot
    print("Step 2: SNAPSHOT")
    print("───────────────────────────────────────────────────")
    week = datetime.utcnow().strftime("%Y-W%V")
    snapshot_file = EVALUATIONS_DIR / f"{week}.json"
    EVALUATIONS_DIR.mkdir(parents=True, exist_ok=True)

    evaluation['snapshot_time'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(snapshot_file, 'w') as f:
        json.dump(evaluation, f, indent=2)
    print(f"Saved: {snapshot_file}")
    print()

    # Step 3: Evolve
    print("Step 3: EVOLVE")
    print("───────────────────────────────────────────────────")
    if under or failing:
        cmd_apply()
    else:
        print("All skills are healthy. No evolution needed.")

    print()
    print("═══════════════════════════════════════════════════")
    print("EVOLUTION CYCLE COMPLETE")
    print("═══════════════════════════════════════════════════")


def main():
    if len(sys.argv) < 2:
        print("Darwin Evolution Engine")
        print()
        print("Usage:")
        print("  python evolve.py status   - Show fitness scores")
        print("  python evolve.py suggest  - Show mutation suggestions")
        print("  python evolve.py apply    - Apply mutations to underperformers")
        print("  python evolve.py cycle    - Full evolution cycle")
        return

    cmd = sys.argv[1]

    if cmd == "status":
        cmd_status()
    elif cmd == "suggest":
        cmd_suggest()
    elif cmd == "apply":
        cmd_apply()
    elif cmd == "cycle":
        cmd_cycle()
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
