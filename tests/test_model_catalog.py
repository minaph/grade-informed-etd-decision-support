from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from list_models import model_catalog


class ModelCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.models = self.root / "references/models"
        self.models.mkdir(parents=True)

    def write(self, name, content):
        path = self.models / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_discovers_new_nested_models_and_preserves_yaml_registry(self):
        self.write("explanation.md", "---\nname: explain\ndescription: 説明\nkind: report-model\n---\n# Body\n")
        self.write("etd/profiles.yaml", "name: profiles\ndescription: Profiles\nkind: registry\nprofiles: []\n")
        entries, errors = model_catalog(self.root)
        self.assertEqual(errors, [])
        self.assertEqual({e["name"] for e in entries}, {"explain", "profiles"})
        self.assertEqual(entries[0]["path"], "references/models/etd/profiles.yaml")
        self.assertEqual(entries[1]["description"], "説明")

    def test_missing_or_unclosed_frontmatter_is_rejected(self):
        for content in ("# Model", "---\nname: model\n"):
            with self.subTest(content=content):
                self.write("model.md", content)
                self.assertTrue(model_catalog(self.root)[1])

    def test_malformed_metadata_is_rejected(self):
        for content in ("[", "- item", "name: m\ndescription: ''\nkind: report-model",
                        "name: m\ndescription: 42\nkind: report-model",
                        "name: m\ndescription: Text\nkind: unknown"):
            with self.subTest(content=content):
                self.write("model.yaml", content)
                self.assertTrue(model_catalog(self.root)[1])

    def test_duplicate_names_are_rejected(self):
        for name in ("a.md", "nested/b.md"):
            self.write(name, "---\nname: repeated\ndescription: Text\nkind: domain-model\n---\n")
        self.assertIn("duplicate name", model_catalog(self.root)[1][0])

    def test_empty_catalog_is_rejected(self):
        self.assertTrue(model_catalog(self.root)[1])
