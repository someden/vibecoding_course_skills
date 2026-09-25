#!/usr/bin/env python3
"""Check this repo's flat frontmatter and resources after isolated skill copying.

Only Python's standard library is required. This is a repository check, not a full
YAML/Agent Skills validator; exercise the real Skills CLI for discovery as well.
"""

import argparse
import json
from pathlib import Path
import re
import shutil
import tempfile


ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
RESOURCE = re.compile(r"(?<![\w./])(?:\.\.?/)*(?:references|agents)/[\w./-]+\.(?:md|json|yaml|py|sh)")
LINK = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)\)")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    parts = text.split("---\n", 2)
    require(len(parts) == 3 and not parts[0], f"{path}: missing frontmatter")
    fields = {}
    for line in parts[1].splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([a-z][a-z-]*):\s*(.+)", line)
        require(match, f"{path}: expected flat scalar frontmatter: {line}")
        key, value = match.groups()
        require(key not in fields, f"{path}: duplicate field {key}")
        if value.startswith('"'):
            value = json.loads(value)
        require(isinstance(value, str) and value.strip(), f"{path}: empty {key}")
        fields[key] = value
    name = fields.get("name", "")
    require(len(name) <= 64 and NAME.fullmatch(name), f"{path}: invalid name")
    description = fields.get("description", "")
    require(1 <= len(description) <= 1024, f"{path}: description length {len(description)}")
    require("../" not in description, f"{path}: relative path in description")
    return fields


def check_references(skill):
    for path in skill.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        # Templates and example documents contain paths for the target project.
        prose = re.sub(r"```.*?```", "", text, flags=re.S)
        links = set(RESOURCE.findall(prose))
        links.update(link for link in LINK.findall(prose)
                     if not link.startswith(("https:", "http:", "#", "mailto:")))
        for link in links:
            target = (path.parent / link.split("#", 1)[0]).resolve()
            require(target.is_relative_to(skill.resolve()), f"{path}: resource escapes skill: {link}")
            require(target.is_file(), f"{path}: missing resource {link}")


def check(skills_dir):
    entries = sorted(skills_dir.glob("*/SKILL.md"))
    require(entries, f"No skills in {skills_dir}")
    names = set()
    resources = 0
    with tempfile.TemporaryDirectory(prefix="vibecoding-skills-check-") as directory:
        for entry in entries:
            fields = frontmatter(entry)
            name = fields["name"]
            require(entry.parent.name == name, f"{entry}: name differs from directory")
            require(name not in names, f"Duplicate skill: {name}")
            names.add(name)
            for resource in entry.parent.rglob("*"):
                if resource.is_symlink():
                    require(resource.exists(), f"Broken symlink: {resource}")
                    require(resource.resolve().is_relative_to(skills_dir.parent.resolve()),
                            f"Symlink outside package: {resource}")
            isolated = Path(directory) / name
            shutil.copytree(entry.parent, isolated, symlinks=False)
            check_references(isolated)
            resources += sum(path.is_file() for path in isolated.rglob("*") if path.name != "SKILL.md")
    return names, resources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=Path, default=ROOT / "skills")
    args = parser.parse_args()
    names, resources = check(args.skills_dir.resolve())
    if args.skills_dir.resolve() == ROOT / "skills":
        # Git checkouts without symlink support may contain only the target text.
        # These files exist but would not deliver the actual instructions.
        for entry in (ROOT / "skills").glob("*/SKILL.md"):
            for source in (ROOT / "skills/_shared").glob("*.md"):
                resource = entry.parent / "references" / source.name
                if resource.exists():
                    require(resource.is_symlink() and resource.resolve() == source.resolve(),
                            f"Expected source symlink: {resource}")
            for resource in (entry.parent / "agents").glob("*.md"):
                require(resource.is_symlink() and resource.resolve() == ROOT / "agents" / resource.name,
                        f"Expected role symlink: {resource}")
        for role in (ROOT / "agents").glob("*.md"):
            frontmatter(role)
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        require(plugin["name"] == marketplace["plugins"][0]["name"], "Plugin names differ")
        require((ROOT / marketplace["plugins"][0]["source"]).resolve() == ROOT, "Invalid plugin source")
        require(re.fullmatch(r"\d+\.\d+\.\d+", plugin["version"]), "Invalid plugin version")
    print(f"OK: {len(names)} skills; {resources} packaged resources; isolated references resolve.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        raise SystemExit(str(error)) from error
