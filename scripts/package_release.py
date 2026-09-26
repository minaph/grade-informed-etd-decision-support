"""Build portable skill ZIPs from the current Git worktree."""
from __future__ import annotations

import argparse
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import zipfile

from portable_content import build_portable_files, is_runtime_path


ARCHIVE_ROOT = "grade-informed-etd-decision-support"


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


def _collect_repository(repository: Path, prefix: PurePosixPath, files: dict[str, bytes]) -> None:
    for mode, object_id, relative in _index_entries(repository):
        source = repository.joinpath(*relative.parts)
        packaged = prefix.joinpath(relative)
        if mode == "160000":
            if source.is_symlink() or not source.is_dir() or not (source / ".git").exists():
                raise PackageError(f"submodule is not initialized: {source}")
            if not source.resolve().is_relative_to(repository.resolve()):
                raise PackageError(f"submodule escapes its repository: {source}")
            child_root = Path(_git_output(source, "rev-parse", "--show-toplevel").strip()).resolve()
            if child_root != source.resolve():
                raise PackageError(f"submodule is not initialized: {source}")
            actual = _git_output(source, "rev-parse", "HEAD").strip()
            if actual != object_id:
                raise PackageError(f"submodule pin mismatch: {source} is {actual}, expected {object_id}")
            _require_clean_submodule(source)
            _collect_repository(source, packaged, files)
            continue
        if not is_runtime_path(packaged):
            continue
        if source.is_symlink():
            raise PackageError(f"runtime file cannot be a symlink: {source}")
        if not source.resolve(strict=False).is_relative_to(repository.resolve()) or not source.is_file():
            raise PackageError(f"runtime file is missing or escapes its repository: {source}")
        key = packaged.as_posix()
        if key in files:
            raise PackageError(f"duplicate runtime file: {key}")
        files[key] = source.read_bytes()


def _collect_runtime_files(root: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    _collect_repository(root, PurePosixPath(), files)
    if not files:
        raise PackageError("Git worktree has no runtime files")
    return files


def _archive_name(path: str, layout: str) -> str:
    relative = _safe_relative(path)
    if layout == "folder":
        return PurePosixPath(ARCHIVE_ROOT).joinpath(relative).as_posix()
    return relative.as_posix()


def build_archive(root: Path, output: Path, layout: str = "folder") -> Path:
    """Create an atomic portable ZIP in the requested layout."""
    if layout not in {"folder", "flat"}:
        raise PackageError(f"unsupported archive layout: {layout}")
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
        if any(mode == "160000" and output_relative.is_relative_to(relative)
               for mode, _, relative in _index_entries(root)):
            raise PackageError(f"archive output cannot be inside a submodule: {output}")
        tracked_output = _git(root, "ls-files", "--error-unmatch", "--", output_relative.as_posix())
        if tracked_output.returncode == 0:
            raise PackageError(f"archive output would overwrite a source path: {output}")

    portable_files = build_portable_files(_collect_runtime_files(root))
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
            for path, content in sorted(portable_files.items()):
                archive.writestr(_archive_name(path, layout), content)
        os.replace(temporary, output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return output


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Create a portable skill ZIP from tracked Git files.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist") / f"{ARCHIVE_ROOT}.zip",
        help="archive path relative to the repository root (default: %(default)s)",
    )
    parser.add_argument(
        "--layout",
        choices=("folder", "flat"),
        default="folder",
        help="place files below the package folder or directly in the ZIP root",
    )
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else root / args.output
    try:
        archive = build_archive(root, output, args.layout)
    except (PackageError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Created {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
