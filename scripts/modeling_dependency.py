from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess

import yaml

MODELING_PATH = Path("skills/conceptual-modeling")


def package_files(root: Path) -> dict[str, Path]:
    """The parent manifest covers its files; Git pins the child separately."""
    files = {}
    for directory, dirs, names in os.walk(root):
        current = Path(directory)
        dirs[:] = [
            name for name in dirs
            if name not in {".git", "__pycache__", ".test-deps"}
            and (current / name).relative_to(root) != MODELING_PATH
        ]
        for name in names:
            path = current / name
            if name == ".git" or path.suffix == ".pyc" or path == root / "MANIFEST.sha256":
                continue
            files["./" + path.relative_to(root).as_posix()] = path
    return files


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )


def validate_modeling_dependency(root: Path) -> list[str]:
    errors = []
    child = root / MODELING_PATH
    entry = git(root, "ls-files", "--stage", "--", MODELING_PATH.as_posix())
    match = re.fullmatch(r"160000 ([0-9a-f]{40,64}) 0\t" + re.escape(MODELING_PATH.as_posix()) + r"\n", entry.stdout)
    if entry.returncode or not match:
        return ["conceptual-modeling must be a pinned git submodule in the index"]
    config = "submodule.skills/conceptual-modeling"
    path_config = git(root, "config", "-f", ".gitmodules", "--get", config + ".path")
    url_config = git(root, "config", "-f", ".gitmodules", "--get", config + ".url")
    if path_config.returncode or path_config.stdout.strip() != MODELING_PATH.as_posix() or url_config.returncode or not url_config.stdout.strip():
        errors.append("conceptual-modeling needs its path and clone URL in .gitmodules")
    if not (child / ".git").exists() or child.is_symlink():
        return errors + ["conceptual-modeling is not initialized; run git submodule update --init --recursive"]
    top = git(child, "rev-parse", "--show-toplevel")
    if top.returncode or Path(top.stdout.strip()).resolve() != child.resolve():
        return errors + ["conceptual-modeling is not its own git checkout"]
    head = git(child, "rev-parse", "HEAD")
    if head.returncode or head.stdout.strip() != match.group(1):
        errors.append("conceptual-modeling checkout differs from the pinned commit")
    status = git(child, "status", "--porcelain", "--untracked-files=all", "--ignore-submodules=none")
    if status.returncode or status.stdout.strip():
        errors.append("conceptual-modeling has uncommitted or untracked changes")
    skill = child / "SKILL.md"
    if not skill.is_file():
        return errors + ["conceptual-modeling/SKILL.md is missing"]
    text = skill.read_text(encoding="utf-8")
    try:
        meta = yaml.safe_load(text.split("---", 2)[1]) if text.startswith("---\n") and text.count("---") >= 2 else None
    except yaml.YAMLError:
        meta = None
    if not isinstance(meta, dict) or meta.get("name") != "conceptual-modeling" or not isinstance(meta.get("description"), str) or not meta["description"].strip():
        errors.append("conceptual-modeling requires matching name and a non-empty description")
    if len(text.splitlines()) >= 500:
        errors.append("conceptual-modeling/SKILL.md should remain below 500 lines")
    for document in child.rglob("*.md"):
        if ".git" in document.relative_to(child).parts:
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            destination = (document.parent / target.split("#", 1)[0]).resolve()
            if not destination.is_relative_to(child.resolve()) or not destination.is_file():
                errors.append(f"child reference is missing or escapes its skill: {document.name}: {target}")
    return errors
