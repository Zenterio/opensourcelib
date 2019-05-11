import unittest
from unittest.mock import patch

from ..types import Choice, Entity, Flag, GlobPattern, Path


class TestConfigTypes(unittest.TestCase):

    def test_path_with_exists_true_when_path_does_exist(self):
        with patch('os.path.exists', return_value=True):
            Path(exists=True)('path/that/exists')

    def test_path_with_exists_true_when_path_does_not_exist(self):
        with patch('os.path.exists', return_value=False):
            self.assertRaises(TypeError, Path(exists=True), 'path/that/does/not/exists')

    def test_path_with_exists_false(self):
        Path(exists=False)('path/that/exists')

    def test_choice_in_choices(self):
        Choice(['a', 'b', 'c'])('c')

    def test_choice_not_in_choices(self):
        self.assertRaises(TypeError, Choice(['a', 'b', 'c']), 'd')

    def test_glob_pattern_with_exists_match_false(self):
        GlobPattern(False)('pattern/matching/path/that/exists')

    def test_glob_pattern_with_exist_match_true(self):
        with patch('glob.glob', return_value=['pattern/matching/path/that/exists']):
            GlobPattern(True)('pattern/matching/path/that/exists')

    def test_glob_pattern_with_exist_match_true_and_non_matching_pattern(self):
        with self.assertRaises(TypeError), \
             patch('glob.glob', return_value=[]):
            GlobPattern(True)('pattern/matching/path/that/does/not/exist')

    def test_flag(self):
        self.assertTrue(Flag()(True))
        self.assertFalse(Flag()(False))

    def test_entity(self):
        self.assertEqual(Entity()('ab'), 'ab')

    def test_entity_with_upper_case(self):
        with self.assertRaises(TypeError):
            Entity()('AB')

    def test_entity_with_dash(self):
        with self.assertRaises(TypeError):
            Entity()('a-b')

    def test_entity_with_underscore(self):
        with self.assertRaises(TypeError):
            Entity()('a_b')
