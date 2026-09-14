from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from modeling_dependency import package_files, validate_modeling_dependency

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Agent Skill package itself.")
    parser.add_argument("--require-skills-ref", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    skill_path = ROOT / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or text.count("---") < 2:
        errors.append("SKILL.md frontmatter is missing")
        meta = {}
    else:
        meta = yaml.safe_load(text.split("---", 2)[1]) or {}
    skill_name = meta.get("name")
    if not isinstance(skill_name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill_name):
        errors.append("frontmatter name must be a non-empty hyphen-case skill name")
    elif ROOT.name != skill_name and not re.fullmatch(r"skill-[a-z0-9]+", ROOT.name):
        errors.append("the skill directory must use the frontmatter name or a reconciled skill-* name")
    if not meta.get("description"):
        errors.append("description is required")
    if set(meta) != {"name", "description"}:
        errors.append("frontmatter may contain only name and description")
    if len(text.splitlines()) >= 500:
        errors.append("SKILL.md should remain below 500 lines")
    if "$SKILL_DIR" in text:
        errors.append("use skill-root-relative paths rather than $SKILL_DIR")

    schema = json.loads((ROOT / "assets/canonical-etd-schema.json").read_text(encoding="utf-8"))
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        errors.append(f"invalid JSON Schema: {exc}")

    manifest_path = ROOT / "MANIFEST.sha256"
    manifest_entries: dict[str, str] = {}
    for line_number, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), 1):
        parts = line.split("  ", 1)
        if len(parts) != 2 or not parts[1].startswith("./"):
            errors.append(f"invalid manifest line {line_number}")
            continue
        digest, relative = parts
        if relative in manifest_entries:
            errors.append(f"duplicate manifest path: {relative}")
        manifest_entries[relative] = digest
    parent_files = package_files(ROOT)
    missing_manifest = sorted(set(parent_files) - set(manifest_entries))
    stale_manifest = sorted(set(manifest_entries) - set(parent_files))
    if missing_manifest:
        errors.append(f"manifest is missing files: {missing_manifest}")
    if stale_manifest:
        errors.append(f"manifest lists absent or excluded files: {stale_manifest}")
    for relative, path in parent_files.items():
        expected = manifest_entries.get(relative)
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if expected is not None and expected.lower() != actual:
            errors.append(f"manifest hash mismatch: {relative}")

    errors.extend(validate_modeling_dependency(ROOT))

    eval_result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_evals.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if eval_result.returncode:
        errors.append(eval_result.stdout + eval_result.stderr)

    profile_result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_profiles.py"), "--registry-only"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if profile_result.returncode:
        errors.append(profile_result.stdout + profile_result.stderr)

    executable = shutil.which("skills-ref") or shutil.which("agentskills")
    if executable:
        validation_path = ROOT
        temp_dir = None
        if isinstance(skill_name, str) and ROOT.name != skill_name:
            temp_dir = tempfile.TemporaryDirectory(prefix=".skills-ref-", dir=ROOT.parent)
            validation_path = Path(temp_dir.name) / skill_name
            validation_path.symlink_to(ROOT, target_is_directory=True)
        try:
            completed = subprocess.run(
                [executable, "validate", str(validation_path)],
                cwd=ROOT.parent,
                text=True,
                capture_output=True,
                check=False,
            )
        finally:
            if temp_dir is not None:
                temp_dir.cleanup()
        if completed.returncode:
            errors.append("skills-ref validation failed:\n" + completed.stdout + completed.stderr)
        child_validation = subprocess.run(
            [executable, "validate", str(ROOT / "skills/conceptual-modeling")],
            capture_output=True, text=True, check=False,
        )
        if child_validation.returncode:
            errors.append("child skills-ref validation failed:\n" + child_validation.stdout + child_validation.stderr)
    elif args.require_skills_ref:
        errors.append("skills-ref is required but unavailable")
    else:
        warnings.append("skills-ref executable unavailable; run it in release CI")

    for warning in warnings:
        print(f"WARNING PACKAGE: {warning}")
    for error in errors:
        print(f"ERROR PACKAGE: {error}")
    if errors:
        return 1
    print("OK: package frontmatter, schema, profiles, domain packs, and eval definitions are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
