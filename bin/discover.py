#!/usr/bin/env python3
"""
Darwin Skill Discovery - Fetch trending skills from multiple sources
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

DARWIN_DIR = Path.home() / ".claude" / "darwin"
SKILLS_DIR = DARWIN_DIR / "skills"
DISCOVERY_CACHE = DARWIN_DIR / "discovery"

# Primary source (may not be available)
SKILLS_SH_URL = "https://skills.sh/trending"

# GitHub API for searching Claude Code related repos
GITHUB_API_URL = "https://api.github.com/search/repositories"

# Curated fallback skills - popular Claude Code extensions & patterns
CURATED_SKILLS = [
    {
        "source": "anthropics/claude-code-skills",
        "skill_id": "pdf",
        "name": "PDF Handler",
        "installs": 15000,
        "description": "Read, merge, split PDFs with Claude Code",
        "install_cmd": "Built-in skill - enable in Claude settings"
    },
    {
        "source": "anthropics/claude-code-skills",
        "skill_id": "docx",
        "name": "Word Documents",
        "installs": 12000,
        "description": "Create/edit Word docs with tracked changes",
        "install_cmd": "Built-in skill - enable in Claude settings"
    },
    {
        "source": "anthropics/claude-code-skills",
        "skill_id": "xlsx",
        "name": "Excel Spreadsheets",
        "installs": 11000,
        "description": "Create spreadsheets with working formulas",
        "install_cmd": "Built-in skill - enable in Claude settings"
    },
    {
        "source": "community/code-review",
        "skill_id": "code-review",
        "name": "Code Review Assistant",
        "installs": 8500,
        "description": "Thorough PR reviews with security focus",
        "install_cmd": "Create ~/.claude/commands/review.md"
    },
    {
        "source": "community/test-generator",
        "skill_id": "test-gen",
        "name": "Test Generator",
        "installs": 7200,
        "description": "Generate unit tests matching project patterns",
        "install_cmd": "Create ~/.claude/commands/test-gen.md"
    },
    {
        "source": "community/api-docs",
        "skill_id": "api-docs",
        "name": "API Documentation",
        "installs": 6800,
        "description": "Generate OpenAPI specs from code",
        "install_cmd": "Create ~/.claude/commands/api-docs.md"
    },
    {
        "source": "community/migration",
        "skill_id": "migrate",
        "name": "Code Migration",
        "installs": 5500,
        "description": "Migrate between frameworks/versions",
        "install_cmd": "Create ~/.claude/commands/migrate.md"
    },
    {
        "source": "community/refactor",
        "skill_id": "refactor",
        "name": "Smart Refactor",
        "installs": 5200,
        "description": "Safe refactoring with dependency tracking",
        "install_cmd": "Create ~/.claude/commands/refactor.md"
    },
    {
        "source": "community/perf-audit",
        "skill_id": "perf",
        "name": "Performance Audit",
        "installs": 4800,
        "description": "Find performance bottlenecks",
        "install_cmd": "Create ~/.claude/commands/perf.md"
    },
    {
        "source": "community/changelog",
        "skill_id": "changelog",
        "name": "Changelog Generator",
        "installs": 4500,
        "description": "Generate changelogs from git history",
        "install_cmd": "Create ~/.claude/commands/changelog.md"
    },
]

# Categories to match against your usage patterns
SKILL_CATEGORIES = {
    "react": ["react", "frontend", "component", "ui"],
    "testing": ["test", "jest", "vitest", "cypress"],
    "devops": ["docker", "ci", "deploy", "kubernetes"],
    "database": ["database", "sql", "postgres", "mongo"],
    "api": ["api", "rest", "graphql", "endpoint"],
    "design": ["design", "css", "tailwind", "styling"],
    "docs": ["documentation", "readme", "docs"],
    "security": ["security", "auth", "oauth"],
}


def fetch_from_skills_sh():
    """Fetch trending skills from skills.sh (primary source)"""
    try:
        req = urllib.request.Request(
            SKILLS_SH_URL,
            headers={"User-Agent": "Darwin-Skills/1.1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8")

        skills = []
        pattern = r'\{"source":"([^"]+)","skillId":"([^"]+)","name":"([^"]+)","installs":(\d+)\}'
        matches = re.findall(pattern, html)

        for match in matches:
            source, skill_id, name, installs = match
            skills.append({
                "source": source,
                "skill_id": skill_id,
                "name": name,
                "installs": int(installs),
                "install_cmd": f"npx skills add {source}"
            })

        return skills
    except Exception:
        return None


def fetch_from_github():
    """Fetch Claude Code related repos from GitHub API (fallback)"""
    try:
        queries = [
            "claude+code+skill",
            "claude+code+command",
            "anthropic+claude+mcp",
        ]

        all_repos = []
        for query in queries[:1]:  # Just first query to avoid rate limits
            url = f"{GITHUB_API_URL}?q={query}&sort=stars&per_page=10"
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Darwin-Skills/1.1.0",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            for repo in data.get("items", []):
                all_repos.append({
                    "source": repo["full_name"],
                    "skill_id": repo["name"],
                    "name": repo["name"].replace("-", " ").title(),
                    "installs": repo["stargazers_count"],
                    "description": repo.get("description", "")[:80] if repo.get("description") else "",
                    "install_cmd": f"git clone {repo['html_url']}"
                })

        return all_repos
    except Exception:
        return None


def fetch_trending_skills():
    """Fetch trending skills from multiple sources with fallbacks"""
    print("Fetching skill recommendations...")
    print()

    # Try skills.sh first
    print("  → Checking skills.sh...", end=" ")
    skills = fetch_from_skills_sh()
    if skills:
        print(f"found {len(skills)} skills")
        return skills
    print("unavailable")

    # Try GitHub API
    print("  → Checking GitHub...", end=" ")
    skills = fetch_from_github()
    if skills:
        print(f"found {len(skills)} repos")
        # Merge with curated list
        combined = skills + CURATED_SKILLS
        # Deduplicate
        seen = set()
        unique = []
        for s in combined:
            if s["skill_id"] not in seen:
                seen.add(s["skill_id"])
                unique.append(s)
        unique.sort(key=lambda x: x["installs"], reverse=True)
        return unique
    print("rate limited or unavailable")

    # Use curated fallback
    print("  → Using curated skill list")
    print()
    return CURATED_SKILLS.copy()


def get_installed_skills():
    """Get list of currently installed Darwin skills"""
    installed = []
    if SKILLS_DIR.exists():
        for f in SKILLS_DIR.glob("*.yaml"):
            installed.append(f.stem)
    return installed


def categorize_skill(skill_name):
    """Categorize a skill based on its name"""
    name_lower = skill_name.lower()
    categories = []
    for cat, keywords in SKILL_CATEGORIES.items():
        if any(kw in name_lower for kw in keywords):
            categories.append(cat)
    return categories if categories else ["general"]


def get_usage_categories():
    """Analyze telemetry to determine user's primary categories"""
    telemetry_file = DARWIN_DIR / "telemetry" / "invocations.jsonl"
    categories = {}

    if telemetry_file.exists():
        try:
            with open(telemetry_file) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            skill = data.get("skill", "")
                            # Map skills to categories
                            if skill in ["plan", "scaffold"]:
                                categories["react"] = categories.get("react", 0) + 1
                            if skill in ["techdebt", "build-fix"]:
                                categories["testing"] = categories.get("testing", 0) + 1
                            if skill in ["commit"]:
                                categories["devops"] = categories.get("devops", 0) + 1
                            if skill in ["rams"]:
                                categories["design"] = categories.get("design", 0) + 1
                        except json.JSONDecodeError:
                            continue
        except Exception:
            pass

    # Return top categories or defaults
    if categories:
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        return [c[0] for c in sorted_cats[:3]]
    return ["react", "design", "testing"]  # defaults


def filter_relevant_skills(skills, installed, user_categories):
    """Filter skills to show most relevant ones"""
    relevant = []

    for skill in skills:
        # Skip already installed
        if skill["skill_id"] in installed:
            continue

        # Check category relevance
        skill_cats = categorize_skill(skill["name"])
        relevance_score = 0

        for cat in skill_cats:
            if cat in user_categories:
                relevance_score += 2
            else:
                relevance_score += 0.5

        # Boost by popularity (log scale)
        import math
        popularity_boost = math.log10(max(skill["installs"], 1)) / 5

        skill["relevance"] = relevance_score + popularity_boost
        skill["categories"] = skill_cats
        relevant.append(skill)

    # Sort by relevance
    relevant.sort(key=lambda x: x["relevance"], reverse=True)
    return relevant[:20]  # Top 20


def save_discovery_cache(skills):
    """Save discovered skills to cache"""
    DISCOVERY_CACHE.mkdir(parents=True, exist_ok=True)
    cache_file = DISCOVERY_CACHE / "trending.json"

    data = {
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "skills": skills
    }

    with open(cache_file, "w") as f:
        json.dump(data, f, indent=2)

    return cache_file


def load_discovery_cache():
    """Load cached discovery data"""
    cache_file = DISCOVERY_CACHE / "trending.json"
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return None


def print_discoveries(skills, show_all=False):
    """Print discovered skills in nice format"""
    print()
    print("═" * 55)
    print("DARWIN SKILL DISCOVERY")
    print("═" * 55)
    print()

    if not skills:
        print("No skills found. Try again later or check your network.")
        return

    display = skills if show_all else skills[:10]

    print(f"TOP {len(display)} RECOMMENDED SKILLS")
    print("─" * 55)
    print()

    for i, skill in enumerate(display, 1):
        installs = skill["installs"]
        if installs >= 1000:
            installs_str = f"{installs/1000:.1f}K"
        else:
            installs_str = str(installs)

        cats = ", ".join(skill.get("categories", ["general"]))
        desc = skill.get("description", "")

        print(f"{i:2}. {skill['name']}")
        if desc:
            print(f"    {desc}")
        print(f"    ⭐ {installs_str} │ {cats}")
        print(f"    └─ {skill['install_cmd']}")
        print()

    print("─" * 55)
    print("To add a skill to Darwin:")
    print("  1. Create a YAML file in ~/.claude/darwin/skills/")
    print("  2. Run: python3 ~/.claude/darwin/bin/compile.py <skill>")
    print("═" * 55)


def main():
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print("Darwin Skill Discovery")
        print()
        print("Usage: discover.py [command]")
        print()
        print("Commands:")
        print("  fetch     Fetch fresh trending skills from skills.sh")
        print("  show      Show cached recommendations (default)")
        print("  all       Show all discovered skills")
        print("  json      Output as JSON")
        return

    command = args[0] if args else "show"

    # Get installed skills and user categories
    installed = get_installed_skills()
    user_categories = get_usage_categories()

    if command == "fetch" or not load_discovery_cache():
        # Fetch fresh data
        all_skills = fetch_trending_skills()
        if all_skills:
            relevant = filter_relevant_skills(all_skills, installed, user_categories)
            save_discovery_cache(relevant)
            print(f"Fetched {len(all_skills)} skills, {len(relevant)} relevant")
            skills = relevant
        else:
            print("Could not fetch skills from skills.sh")
            skills = []
    else:
        # Use cache
        cache = load_discovery_cache()
        skills = cache.get("skills", [])
        print(f"Using cached data from {cache.get('fetched_at', 'unknown')}")

    if command == "json":
        print(json.dumps(skills, indent=2))
    elif command == "all":
        print_discoveries(skills, show_all=True)
    else:
        print_discoveries(skills)


if __name__ == "__main__":
    main()
