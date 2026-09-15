from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"report-model", "domain-model", "methodology", "redirect", "registry"}


def model_catalog(root: Path) -> tuple[list[dict[str, str]], list[str]]:
    """Read discovery metadata from the files themselves, without a second index."""
    entries = []
    errors = []
    names = set()
    paths = sorted(p for p in (root / "references/models").rglob("*")
                   if p.is_file() and p.suffix in {".md", ".yaml", ".yml"})
    if not paths:
        return [], ["No model documents found"]
    for path in paths:
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".md":
                lines = text.splitlines()
                if not lines or lines[0] != "---":
                    raise ValueError("missing frontmatter")
                end = lines.index("---", 1)
                text = "\n".join(lines[1:end])
            meta = yaml.safe_load(text)
            if not isinstance(meta, dict):
                raise ValueError("metadata must be a mapping")
            if any(not isinstance(meta.get(key), str) or not meta[key].strip()
                   for key in ("name", "description", "kind")):
                raise ValueError("name, description, and kind must be non-empty strings")
            if meta["kind"] not in KINDS:
                raise ValueError(f"unknown document kind: {meta['kind']}")
            if meta["name"] in names:
                raise ValueError(f"duplicate name: {meta['name']}")
            names.add(meta["name"])
            entries.append({"path": relative, **{key: meta[key] for key in
                                                ("name", "description", "kind")}})
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(f"{relative}: {exc}")
    return entries, errors


def main() -> int:
    entries, errors = model_catalog(ROOT)
    if errors:
        for error in errors:
            print(f"ERROR MODEL: {error}")
        return 1
    for entry in entries:
        print(f"{entry['path']} [{entry['kind']}] {entry['name']}")
        print(f"  {entry['description']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
