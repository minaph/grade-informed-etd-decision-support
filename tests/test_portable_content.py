from __future__ import annotations

from pathlib import Path, PurePosixPath
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from portable_content import (
    PortableContentError,
    build_portable_files,
    is_runtime_path,
)


def source_files() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = PurePosixPath(path.relative_to(ROOT).as_posix())
        if is_runtime_path(relative):
            files[relative.as_posix()] = path.read_bytes()
    return files


class PortableContentTests(unittest.TestCase):
    def test_selects_only_portable_runtime_files(self) -> None:
        source = source_files()
        source["README.md"] = b"development-only file"
        source[".gitignore"] = b"development-only hidden file"
        files = build_portable_files(source)
        paths = {PurePosixPath(path) for path in files}

        self.assertEqual([path for path in paths if path.name == "SKILL.md"], [PurePosixPath("SKILL.md")])
        self.assertIn(PurePosixPath("skills/conceptual-modeling/GUIDE.md"), paths)
        self.assertIn(PurePosixPath("skills/decision-structuring/GUIDE.md"), paths)
        self.assertIn(PurePosixPath("skills/evidence-based-writing/GUIDE.md"), paths)
        self.assertIn(PurePosixPath("references/models/etd/official-grade-profiles.yaml"), paths)
        self.assertNotIn(PurePosixPath("README.md"), paths)
        self.assertNotIn(PurePosixPath("MANIFEST.sha256"), paths)
        self.assertNotIn(PurePosixPath(".github/workflows/release.yml"), paths)
        for path in paths:
            self.assertTrue(path == PurePosixPath("SKILL.md") or path.suffix in {".md", ".yaml"})
            self.assertFalse(any(part.startswith(".") for part in path.parts))

    def test_rewrites_runtime_guidance_and_removes_child_frontmatter(self) -> None:
        files = build_portable_files(source_files())
        root = files["SKILL.md"].decode("utf-8")
        decision = files["skills/decision-structuring/GUIDE.md"].decode("utf-8")
        conceptual = files["skills/conceptual-modeling/GUIDE.md"].decode("utf-8")
        decision_properties = files["skills/decision-structuring/references/formation-properties.md"].decode("utf-8")
        reference_index = files["references/README.md"].decode("utf-8")
        formation_redirect = files["references/models/formation-properties.md"].decode("utf-8")
        formation_workflow = files["references/question-formation.md"].decode("utf-8")

        self.assertIn("目的に合う同梱ガイド", root)
        self.assertIn("文章作成の同梱ガイド", root)
        self.assertIn("Read and apply the [decision-structuring guide]", root)
        self.assertIn("skills/decision-structuring/GUIDE.md", root)
        self.assertNotIn("git submodule update", root)
        self.assertNotIn("scripts/list_models.py", root)
        self.assertNotIn("Package checks require Python", root)
        self.assertFalse(decision.startswith("---\n"))
        self.assertIn("../conceptual-modeling/GUIDE.md", decision)
        self.assertIn("caller owns\nadoption of any revised definition", decision)
        self.assertIn("The caller decides when to apply this guide and expose the Tree.", decision_properties)
        self.assertNotIn("The caller decides when to invoke the skill", decision_properties)
        self.assertIn("このガイドの手順は、親の作業の一部として適用します。", conceptual)
        self.assertIn("同梱ガイドの手順として適用します。", reference_index)
        self.assertIn("同梱意思決定構造化ガイド", formation_redirect)
        self.assertIn("This parent skill applies that guide", formation_redirect)
        self.assertIn("## Apply the bundled guide", formation_workflow)
        self.assertNotIn("invoke the subskill", formation_workflow)
        for path, content in files.items():
            if path.endswith(".md"):
                self.assertNotIn("skills/conceptual-modeling/SKILL.md", content.decode("utf-8"))
                self.assertNotIn("skills/decision-structuring/SKILL.md", content.decode("utf-8"))
                self.assertNotIn("skills/evidence-based-writing/SKILL.md", content.decode("utf-8"))

    def test_does_not_rewrite_external_skill_urls(self) -> None:
        source = source_files()
        path = "references/adaptation-rules.md"
        source[path] += b"\n[external](https://example.invalid/skills/decision-structuring/SKILL.md)\n"

        files = build_portable_files(source)

        self.assertIn(
            "https://example.invalid/skills/decision-structuring/SKILL.md",
            files[path].decode("utf-8"),
        )

    def test_rejects_missing_required_guidance_and_broken_local_links(self) -> None:
        missing = source_files()
        del missing["references/models/etd/official-grade-profiles.yaml"]
        with self.assertRaisesRegex(PortableContentError, "missing required guidance"):
            build_portable_files(missing)

        linked = source_files()
        linked["references/adaptation-rules.md"] += b"\n[missing local material](not-bundled.md)\n"
        with self.assertRaisesRegex(PortableContentError, "local Markdown link is not bundled"):
            build_portable_files(linked)

    def test_rejects_changed_transformation_anchor(self) -> None:
        source = source_files()
        source["SKILL.md"] = source["SKILL.md"].replace(
            b"git submodule update --init --recursive",
            b"another acquisition command",
        )

        with self.assertRaisesRegex(PortableContentError, "transformation anchor changed"):
            build_portable_files(source)

    def test_runtime_path_allowlist(self) -> None:
        self.assertTrue(is_runtime_path(PurePosixPath("SKILL.md")))
        self.assertTrue(is_runtime_path(PurePosixPath("references/models/health.md")))
        self.assertTrue(is_runtime_path(PurePosixPath("skills/decision-structuring/SKILL.md")))
        self.assertTrue(is_runtime_path(PurePosixPath("skills/decision-structuring/references/workflow.md")))
        self.assertFalse(is_runtime_path(PurePosixPath("README.md")))
        self.assertFalse(is_runtime_path(PurePosixPath(".github/workflows/release.yml")))
        self.assertFalse(is_runtime_path(PurePosixPath("skills/decision-structuring/README.md")))
        self.assertFalse(is_runtime_path(PurePosixPath("references/private.txt")))


if __name__ == "__main__":
    unittest.main()
