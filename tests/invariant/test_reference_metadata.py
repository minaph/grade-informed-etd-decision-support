from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))

from validate_profiles import load_registry, resolve_profile, validate_registry


class ReferenceMetadataTests(unittest.TestCase):
    def setUp(self):
        self.registry = copy.deepcopy(load_registry())

    def test_registry_and_inherited_template(self):
        self.assertEqual([], validate_registry(self.registry))
        population = resolve_profile('grade.clinical.population_recommendation', self.registry)
        individual = resolve_profile('grade.clinical.individual_recommendation', self.registry)
        self.assertIn('resources', population['include_criteria'])
        self.assertNotIn('resources', individual['include_criteria'])
        self.assertIn('desirable_effects', individual['include_criteria'])
        self.assertEqual(population['source_refs'], individual['source_refs'])

    def test_unknown_parent_and_cycle(self):
        for parent in ('missing', self.registry['profiles'][0]['profile_id']):
            with self.subTest(parent=parent):
                self.registry['profiles'][0]['extends'] = parent
                self.assertTrue(validate_registry(self.registry))

    def test_duplicate_profile(self):
        self.registry['profiles'].append(copy.deepcopy(self.registry['profiles'][0]))
        self.assertTrue(validate_registry(self.registry))

    def test_unknown_source(self):
        self.registry['profiles'][0]['source_refs'] = ['missing-source']
        self.assertTrue(validate_registry(self.registry))

    def test_duplicate_source(self):
        self.registry['source_catalog'].append(copy.deepcopy(self.registry['source_catalog'][0]))
        self.assertTrue(validate_registry(self.registry))

    def test_unknown_criterion_in_exclusion(self):
        self.registry['profiles'][0]['exclude_criteria'].append('missing-criterion')
        self.assertTrue(validate_registry(self.registry))

    def test_conflicting_criteria(self):
        profile = self.registry['profiles'][0]
        profile['exclude_criteria'].append(profile['include_criteria'][0])
        self.assertTrue(validate_registry(self.registry))

    def test_malformed_reference_metadata(self):
        for key, value in [('source_refs', 'not-a-list'), ('perspective', 'unknown')]:
            with self.subTest(key=key):
                data = copy.deepcopy(self.registry)
                data['profiles'][0][key] = value
                self.assertTrue(validate_registry(data))


if __name__ == '__main__':
    unittest.main()
