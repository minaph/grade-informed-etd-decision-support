"""Build a release ZIP from the current Git worktree."""
from __future__ import annotations

import argparse
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile
import zipfile


ARCHIVE_ROOT = "grade-informed-etd-decision-support"
EXCLUDED_DIRECTORIES = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".test-deps",
    ".tox",
    ".venv",
    "build",
    "dist",
    "venv",
}
PRIVATE_FILE_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".ppk"}


class PackageError(RuntimeError):
    """Raised when the worktree cannot safely produce a release archive."""


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _git_output(root: Path, *args: str) -> str:
    completed = _git(root, *args)
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown Git error"
        raise PackageError(f"Git command failed ({' '.join(args)}): {detail}")
    return completed.stdout


def _safe_relative(path: str) -> PurePosixPath:
    relative = PurePosixPath(path)
    if relative.is_absolute() or not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        raise PackageError(f"Git returned an unsafe path: {path!r}")
    return relative


def _is_excluded(relative: PurePosixPath) -> bool:
    if any(part in EXCLUDED_DIRECTORIES for part in relative.parts):
        return True
    name = relative.name.lower()
    return (
        name == ".env"
        or name.startswith(".env.")
        or name == ".ds_store"
        or name == ".coverage"
        or name in {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}
        or name.endswith(".zip")
        or any(name.endswith(suffix) for suffix in PRIVATE_FILE_SUFFIXES)
    )


def _index_entries(root: Path) -> list[tuple[str, str, PurePosixPath]]:
    entries: list[tuple[str, str, PurePosixPath]] = []
    seen: set[PurePosixPath] = set()
    for record in _git_output(root, "ls-files", "--stage", "-z").split("\0"):
        if not record:
            continue
        try:
            metadata, name = record.split("\t", 1)
            mode, object_id, stage = metadata.split(" ", 2)
        except ValueError as error:
            raise PackageError(f"Git returned an invalid index entry: {record!r}") from error
        if stage != "0":
            raise PackageError(f"Git index has unresolved entry: {name}")
        relative = _safe_relative(name)
        if relative in seen:
            raise PackageError(f"Git index contains duplicate entry: {name}")
        seen.add(relative)
        entries.append((mode, object_id, relative))
    return entries


def _write_symlink(archive: zipfile.ZipFile, source: Path, destination: str, root: Path) -> None:
    target = os.readlink(source)
    if Path(target).is_absolute() or not (root / source.relative_to(root).parent / target).resolve(strict=False).is_relative_to(root):
        raise PackageError(f"symlink escapes its repository: {source}")
    info = zipfile.ZipInfo(destination)
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    archive.writestr(info, target.encode("utf-8"))


def _require_clean_submodule(repository: Path) -> None:
    """Reject tracked changes while allowing untracked files to remain excluded."""
    staged = _git(repository, "diff", "--cached", "--quiet", "--ignore-submodules=none")
    if staged.returncode == 1:
        raise PackageError(f"submodule has staged changes: {repository}")
    if staged.returncode:
        detail = staged.stderr.strip() or "unknown Git error"
        raise PackageError(f"cannot inspect submodule index: {repository}: {detail}")

    working_tree = _git(repository, "diff", "--quiet", "--ignore-submodules=all")
    if working_tree.returncode == 1:
        raise PackageError(f"submodule has uncommitted tracked changes: {repository}")
    if working_tree.returncode:
        detail = working_tree.stderr.strip() or "unknown Git error"
        raise PackageError(f"cannot inspect submodule worktree: {repository}: {detail}")


def _add_repository(
    archive: zipfile.ZipFile,
    repository: Path,
    prefix: PurePosixPath,
) -> int:
    written = 0
    for mode, object_id, relative in _index_entries(repository):
        source = repository.joinpath(*relative.parts)
        archive_relative = prefix.joinpath(relative)
        if _is_excluded(archive_relative):
            continue
        if mode == "120000":
            if not source.is_symlink():
                raise PackageError(f"tracked symlink is missing: {source}")
            _write_symlink(archive, source, archive_relative.as_posix(), repository)
            written += 1
            continue
        if not source.resolve(strict=False).is_relative_to(repository.resolve()):
            raise PackageError(f"tracked path escapes its repository: {source}")
        if mode == "160000":
            if source.is_symlink() or not source.is_dir():
                raise PackageError(f"submodule is not initialized: {source}")
            if not (source / ".git").exists():
                raise PackageError(f"submodule is not initialized: {source}")
            child_root = Path(_git_output(source, "rev-parse", "--show-toplevel").strip()).resolve()
            if child_root != source.resolve():
                raise PackageError(f"submodule is not initialized: {source}")
            actual = _git_output(source, "rev-parse", "HEAD").strip()
            if actual != object_id:
                raise PackageError(f"submodule pin mismatch: {source} is {actual}, expected {object_id}")
            _require_clean_submodule(source)
            written += _add_repository(archive, source, archive_relative)
            continue
        if not source.is_file() or source.is_symlink():
            raise PackageError(f"tracked file is missing or unsafe: {source}")
        archive.write(source, archive_relative.as_posix())
        written += 1
    return written


def build_archive(root: Path, output: Path) -> Path:
    """Create an atomic ZIP containing tracked files and pinned submodules."""
    root = root.resolve()
    top_level = _git_output(root, "rev-parse", "--show-toplevel").strip()
    if Path(top_level).resolve() != root:
        raise PackageError(f"package root is not a Git worktree root: {root}")

    output = output.resolve()
    if output.suffix.lower() != ".zip":
        raise PackageError(f"archive output must use a .zip extension: {output}")
    if output.exists() and output.is_dir():
        raise PackageError(f"archive output is a directory: {output}")
    if output.is_relative_to(root):
        output_relative = output.relative_to(root)
        if ".git" in output_relative.parts:
            raise PackageError(f"archive output cannot be inside .git: {output}")
        tracked_output = _git(root, "ls-files", "--error-unmatch", "--", output_relative.as_posix())
        if tracked_output.returncode == 0:
            raise PackageError(f"archive output would overwrite a source path: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=output.parent,
        prefix=f".{output.name}.",
        suffix=".tmp",
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, strict_timestamps=False) as archive:
            written = _add_repository(archive, root, PurePosixPath(ARCHIVE_ROOT))
            if not written:
                raise PackageError("Git worktree has no packageable tracked files")
        os.replace(temporary, output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return output


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Create a release ZIP from tracked Git files.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist") / f"{ARCHIVE_ROOT}.zip",
        help="archive path relative to the repository root (default: %(default)s)",
    )
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else root / args.output
    try:
        archive = build_archive(root, output)
    except PackageError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Created {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
