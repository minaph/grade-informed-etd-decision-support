"""Build the runtime-only files shared by Codex, Claude, and Gemini packages."""
from __future__ import annotations

from pathlib import PurePosixPath
import re
from typing import Mapping


CHILD_SKILLS = (
    "conceptual-modeling",
    "decision-structuring",
    "evidence-based-writing",
)
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FRONTMATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.DOTALL)
URL = re.compile(r"https?://[^\s<>()]+")


class PortableContentError(ValueError):
    """Raised when the portable runtime bundle would be incomplete or unsafe."""


def _safe_path(path: str | PurePosixPath) -> PurePosixPath:
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or not candidate.parts or any(part in {"", ".", ".."} for part in candidate.parts):
        raise PortableContentError(f"portable path is unsafe: {path!s}")
    return candidate


def is_runtime_path(path: PurePosixPath) -> bool:
    """Return whether a source-relative path belongs in a portable skill bundle."""
    path = _safe_path(path)
    if path == PurePosixPath("SKILL.md"):
        return True
    if path.parts[0] == "references":
        return path.suffix in {".md", ".yaml"} and all(not part.startswith(".") for part in path.parts)
    if len(path.parts) < 3 or path.parts[0] != "skills" or path.parts[1] not in CHILD_SKILLS:
        return False
    if path.parts[2] == "SKILL.md" and len(path.parts) == 3:
        return True
    return (
        len(path.parts) >= 4
        and path.parts[2] == "references"
        and path.suffix in {".md", ".yaml"}
        and all(not part.startswith(".") for part in path.parts)
    )


def _decode(path: PurePosixPath, content: bytes) -> str:
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise PortableContentError(f"portable text file is not UTF-8: {path}") from error


def _replace_required(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise PortableContentError(f"portable transformation anchor changed: {label}")
    return text.replace(old, new)


def _replace_local_skill_paths(text: str) -> str:
    """Rewrite local child-SKILL references while leaving external URLs untouched."""
    protected: list[str] = []

    def protect(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"\x00URL{len(protected) - 1}\x00"

    text = URL.sub(protect, text)
    for name in CHILD_SKILLS:
        text = text.replace(f"skills/{name}/SKILL.md", f"skills/{name}/GUIDE.md")
    for index, value in enumerate(protected):
        text = text.replace(f"\x00URL{index}\x00", value)
    return text


def _has_local_old_skill_path(text: str, name: str) -> bool:
    text = URL.sub("", text)
    return f"skills/{name}/SKILL.md" in text


def _transform_root_skill(text: str) -> str:
    text = _replace_required(
        text,
        "モデリング、意思決定構造化、文章作成のサブスキルを目的に応じて参照し、判断と説明を支援します。",
        "モデリング、意思決定構造化、文章作成の同梱ガイドを目的に応じて読み、手順を適用して判断と説明を支援します。",
        "root bundled-guide description",
    )
    text = _replace_required(
        text,
        "Package checks require Python 3.10+ and PyYAML 6+; report writing does not require running scripts.",
        "この配布版は資料を読むだけで利用でき、ローカルの検証環境やスクリプトの実行を必要としません。",
        "root package-check instruction",
    )
    text = _replace_required(
        text,
        "依存先は `skills/` の固定版を使います。未取得の場合は `git submodule update --init --recursive` で初期化します。資料の構造は [references/README.md](references/README.md) に示します。",
        "目的に合う同梱ガイドと [references/README.md](references/README.md) を読み、資料の構造と使い分けを確認します。",
        "root bundled-guides instruction",
    )
    text = _replace_required(
        text,
        "親スキルは、利用目的、事例の情報、必要な成果物をつなぎ、使用する参照モデルとサブスキルを選びます。概念の定義・適用・改訂は `conceptual-modeling`、意思決定の構造化は `decision-structuring`、文章の作成・推敲は `evidence-based-writing` を参照します。各技術の定義はサブスキルに置き、親はそれらを今回の実務へどう結び付けるかを担当します。",
        "親スキルは、利用目的、事例の情報、必要な成果物をつなぎ、使用する参照モデルと同梱ガイドの手順を選びます。概念の定義・適用・改訂には[概念モデリングのガイド](skills/conceptual-modeling/GUIDE.md)、意思決定の構造化には[意思決定構造化のガイド](skills/decision-structuring/GUIDE.md)、文章の作成・推敲には[文章作成・推敲のガイド](skills/evidence-based-writing/GUIDE.md)を読み、必要な手順を適用します。各技術の定義と手順は同梱ガイドに置き、親はそれらを今回の実務へどう結び付けるかを担当します。",
        "root three-guide role instruction",
    )
    text = _replace_required(
        text,
        "親が解釈を担い、意思決定構造化のサブスキルへ渡します。",
        "親が解釈を担い、同梱の意思決定構造化ガイドの手順へ渡します。",
        "root decision-guide handoff",
    )
    text = _replace_required(
        text,
        "Use [decision-structuring](skills/decision-structuring/SKILL.md) for every case\nwithin this skill's scope to generate and retain a minimal `tree_mermaid`.",
        "Read and apply the [decision-structuring guide](skills/decision-structuring/GUIDE.md) for every case\nwithin this skill's scope to generate and retain a minimal `tree_mermaid`.",
        "root required decision-guide procedure",
    )
    text = _replace_required(
        text,
        "一覧は、スキルのルートで次の検索を行うか、ファイルの冒頭を読むことで確認できます。開発用 Python 環境がある場合は `python scripts/list_models.py` も使えます。スクリプトの実行は回答作成の前提ではありません。\n\n```bash\nrg -n '^(name|description|kind):' references/models --glob '*.md' --glob '*.yaml'\n```",
        "一覧は、同梱の `references/models/` 以下にある各ファイルの冒頭を読んで確認します。スクリプトやローカルの検索コマンドを実行する必要はありません。",
        "root local-command instruction",
    )
    return text


def _transform_reference(path: PurePosixPath, text: str) -> str:
    if path == PurePosixPath("references/README.md"):
        text = _replace_required(
            text,
            "基礎となる [概念モデリング](../skills/conceptual-modeling/SKILL.md)、[意思決定構造化](../skills/decision-structuring/SKILL.md)、[文章作成・推敲](../skills/evidence-based-writing/SKILL.md) は、`skills/` の独立サブスキルを参照します。ここではそれらを複製せず、事例へどう適用し、成果へつなげるかを扱います。",
            "基礎となる [概念モデリング](../skills/conceptual-modeling/GUIDE.md)、[意思決定構造化](../skills/decision-structuring/GUIDE.md)、[文章作成・推敲](../skills/evidence-based-writing/GUIDE.md) は、同梱ガイドの手順として適用します。ここではそれらを複製せず、事例へどう適用し、成果へつなげるかを扱います。",
            "reference README bundled-guide procedure",
        )
        text = _replace_required(
            text,
            "メタデータはファイル冒頭の確認や検索で読めます。開発用 Python 環境では `python scripts/list_models.py` で一覧を取得できます。",
            "メタデータは、同梱された各ファイルの冒頭を読んで確認できます。ローカルのスクリプトを実行する必要はありません。",
            "reference README local-command instruction",
        )
    if path == PurePosixPath("references/preset-routing.md"):
        text = _replace_required(
            text,
            "依存先は、親スキルで固定した版を参照します。取得が必要な場合は、READMEのサブモジュール（submodule）取得手順に従います。この文書の `skills/` と `references/` は親スキルのルートから、概念モデリングスキル内の参照はそのスキルのルートから解決します。",
            "依存先は、このパッケージに同梱されたガイドを参照します。この文書の `skills/` と `references/` はパッケージのルートから、概念モデリングのガイド内の参照はそのガイドのルートから解決します。",
            "preset routing bundled-guide instruction",
        )
    if path == PurePosixPath("references/models/formation-properties.md"):
        text = _replace_required(
            text,
            "Context・Questions・Alternatives・Tree の正式な定義を持つ独立した意思決定構造化サブスキルへの参照窓口。定義の複製ではない。",
            "Context・Questions・Alternatives・Tree の正式な定義を持つ同梱意思決定構造化ガイドへの参照窓口。定義の複製ではない。",
            "formation properties guide description",
        )
        text = _replace_required(
            text,
            "The property contract now lives in the reusable\n[decision-structuring subskill](../../skills/decision-structuring/SKILL.md).\nRead its [property model](../../skills/decision-structuring/references/formation-properties.md)\nfor Context, Questions, Alternatives, and the generated Mermaid Tree.\n\nThis parent skill invokes it for every request as an internal diagnostic.",
            "The property contract is defined by the bundled\n[decision-structuring guide](../../skills/decision-structuring/GUIDE.md).\nRead and apply its [property model](../../skills/decision-structuring/references/formation-properties.md)\nfor Context, Questions, Alternatives, and the generated Mermaid Tree.\n\nThis parent skill applies that guide for every request as an internal diagnostic.",
            "formation properties guide procedure",
        )
        text = _replace_required(
            text,
            "The parent owns invocation and visibility.",
            "The parent owns application and visibility.",
            "formation properties parent responsibility",
        )
    if path == PurePosixPath("references/question-formation.md"):
        text = _replace_required(
            text,
            "Use [decision-structuring](../skills/decision-structuring/SKILL.md) to structure,\ncheck, and revise supplied material.",
            "Read and apply the [decision-structuring guide](../skills/decision-structuring/GUIDE.md) to structure,\ncheck, and revise supplied material.",
            "question formation guide procedure",
        )
        text = _replace_required(
            text,
            "It supplies material and consumes the\nsubskill's structured state and missing-information needs. Generic EtD remains\nan external consumer and feedback source; no EtD-specific fields or criterion\nmapping are required by the subskill.",
            "It supplies material and uses the resulting\nstructured state and missing-information needs. Generic EtD remains\nan external consumer and feedback source; no EtD-specific fields or criterion\nmapping are required by the guide.",
            "question formation guide result",
        )
        text = _replace_required(
            text,
            "## Invoke the subskill\n\nFor every parent request, invoke the subskill for a minimal internal diagnostic.",
            "## Apply the bundled guide\n\nFor every parent request, apply the bundled guide for a minimal internal diagnostic.",
            "question formation required guide diagnostic",
        )
        text = _replace_required(
            text,
            "When option\nformation is material, run the subskill's Question formation, Tree projection,\nAlternative formation, and Reverse Projection workflow.",
            "When option\nformation is material, apply the guide's Question formation, Tree projection,\nAlternative formation, and Reverse Projection workflow.",
            "question formation guide workflow",
        )
        text = _replace_required(
            text,
            "revision. One finding can affect both. The subskill regenerates projections and\nreports whether the comparison changed.",
            "revision. One finding can affect both. The guide regenerates projections and\nreports whether the comparison changed.",
            "question formation guide regeneration",
        )
    return text


def _transform_child_guide(name: str, text: str) -> str:
    match = FRONTMATTER.match(text)
    if not match:
        raise PortableContentError(f"child skill has no YAML frontmatter: {name}")
    text = text[match.end() :]
    if name == "conceptual-modeling":
        text = _replace_required(
            text,
            "このスキルは、単独でも、他の作業手順から呼び出しても使えます。呼び出し側は、モデル群の保管場所、聞き取りの時期、成果を後続の判断へ反映する方法を定めます。共有モデルへの正式な反映は、改訂案を確認したうえで、そのモデルの管理・承認手順に従って行います。",
            "このガイドの手順は、親の作業の一部として適用します。親は、モデル群を読む場所、聞き取りの時期、成果を後続の判断へ反映する方法を定めます。共有モデルへの正式な反映は、改訂案を確認したうえで、そのモデルの管理・承認手順に従って行います。",
            "conceptual guide bundled procedure",
        )
    if name == "decision-structuring":
        text = _replace_required(
            text,
            "For substantial assessment or revision of the model itself, consult the\n`conceptual-modeling` skill. The caller provides that skill when needed and\nowns adoption of any revised definition. If it is unavailable, report the\nmodeling need rather than silently rewriting this contract.",
            "For substantial assessment or revision of the model itself, read the\n[conceptual-modeling guide](../conceptual-modeling/GUIDE.md). The caller owns\nadoption of any revised definition. If the required modeling work remains\nunresolved, report that need rather than silently rewriting this contract.",
            "decision guide conceptual-modeling handoff",
        )
    return text


def _transform_child_reference(path: PurePosixPath, text: str) -> str:
    if path == PurePosixPath("skills/decision-structuring/references/formation-properties.md"):
        text = _replace_required(
            text,
            "The caller decides when to invoke the skill and expose the Tree.",
            "The caller decides when to apply this guide and expose the Tree.",
            "decision guide application responsibility",
        )
    return text


def _normalise_relative(path: PurePosixPath) -> PurePosixPath:
    parts: list[str] = []
    for part in path.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if not parts:
                raise PortableContentError(f"local link escapes portable bundle: {path}")
            parts.pop()
        else:
            parts.append(part)
    return PurePosixPath(*parts)


def _validate_markdown_links(files: Mapping[str, bytes]) -> None:
    available = {PurePosixPath(path) for path in files}
    for raw_path, content in files.items():
        path = PurePosixPath(raw_path)
        if path.suffix != ".md":
            continue
        for match in MARKDOWN_LINK.finditer(_decode(path, content)):
            destination = match.group(1).strip()
            if destination.startswith("<") and destination.endswith(">"):
                destination = destination[1:-1]
            destination = destination.split(maxsplit=1)[0]
            if not destination or destination.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target = destination.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            resolved = _normalise_relative(path.parent / PurePosixPath(target))
            if resolved not in available:
                raise PortableContentError(f"local Markdown link is not bundled: {path} -> {destination}")


def _validate_output(files: Mapping[str, bytes]) -> None:
    paths = [PurePosixPath(path) for path in files]
    skill_files = [path for path in paths if path.name == "SKILL.md"]
    if skill_files != [PurePosixPath("SKILL.md")]:
        raise PortableContentError("portable bundle must contain exactly one root SKILL.md")
    for path in paths:
        if path != PurePosixPath("SKILL.md") and (path.suffix not in {".md", ".yaml"} or any(part.startswith(".") for part in path.parts)):
            raise PortableContentError(f"portable bundle has an unsupported runtime path: {path}")
    for name in CHILD_SKILLS:
        guide = PurePosixPath("skills") / name / "GUIDE.md"
        if guide not in paths:
            raise PortableContentError(f"portable bundle is missing child guide: {guide}")
    required = {
        PurePosixPath("references/models/etd/grade-core.md"),
        PurePosixPath("references/models/etd/grade-claim-rules.md"),
        PurePosixPath("references/models/etd/official-grade-profiles.yaml"),
        PurePosixPath("skills/decision-structuring/references/formation-properties.md"),
        PurePosixPath("skills/decision-structuring/references/workflow.md"),
    }
    missing = sorted(required - set(paths))
    if missing:
        raise PortableContentError("portable bundle is missing required guidance: " + ", ".join(map(str, missing)))
    for path, content in files.items():
        if PurePosixPath(path).suffix == ".md":
            for name in CHILD_SKILLS:
                if _has_local_old_skill_path(_decode(PurePosixPath(path), content), name):
                    raise PortableContentError(f"portable Markdown retains old child SKILL path: {path}")
    _validate_markdown_links(files)


def build_portable_files(source_files: dict[str, bytes]) -> dict[str, bytes]:
    """Select and transform source-relative files into a portable runtime bundle."""
    normalised: dict[PurePosixPath, bytes] = {}
    for raw_path, content in source_files.items():
        path = _safe_path(raw_path)
        if path in normalised:
            raise PortableContentError(f"duplicate portable source path: {path}")
        if not isinstance(content, bytes):
            raise PortableContentError(f"portable source content is not bytes: {path}")
        normalised[path] = content

    root_skill = PurePosixPath("SKILL.md")
    if root_skill not in normalised:
        raise PortableContentError("portable source is missing root SKILL.md")
    for name in CHILD_SKILLS:
        child_skill = PurePosixPath("skills") / name / "SKILL.md"
        if child_skill not in normalised:
            raise PortableContentError(f"portable source is missing child skill: {child_skill}")

    output: dict[str, bytes] = {}
    for path, content in normalised.items():
        if not is_runtime_path(path):
            continue
        text = _decode(path, content)
        output_path = path
        if path == root_skill:
            text = _transform_root_skill(text)
        elif path.parts[0] == "references":
            text = _transform_reference(path, text)
        elif path.name == "SKILL.md":
            name = path.parts[1]
            text = _transform_child_guide(name, text)
            output_path = path.with_name("GUIDE.md")
        elif path.parts[0] == "skills":
            text = _transform_child_reference(path, text)
        text = _replace_local_skill_paths(text)
        output[output_path.as_posix()] = text.encode("utf-8")

    _validate_output(output)
    return output
