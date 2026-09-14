"""Refresh hashes of parent files; the child is pinned by the Git index."""
from pathlib import Path
import hashlib

from modeling_dependency import package_files


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    entries = package_files(root)
    (root / "MANIFEST.sha256").write_text(
        "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {name}\n"
                for name, path in sorted(entries.items())),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
