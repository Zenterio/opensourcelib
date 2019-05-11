"""
Tests the classes in the analyzer module.

Note: uses relative imports and hence the parent module need to be loaded.
"""
import re
import unittest

import munch

from ..analyzer import AnalyzerFactory


class TestAnalyzerFactory(unittest.TestCase):

    def _get_definitions(self, config):
        analyzer = AnalyzerFactory().get_analyzer(config)
        return analyzer.trackers[0].definitions

    def test_empty_config_results_in_no_definitions(self):
        config = munch.munchify({'definitions': []})
        definitions = self._get_definitions(config)
        self.assertEqual(0, len(definitions))

    def test_single_definition(self):
        m1 = re.compile('a')
        m2 = re.compile('b')
        config = munch.munchify(
            {
                'definitions': [
                    {
                        'markers': [m1, m2],
                        'invalidators': [m1, m2],
                        'title': 'Title',
                        'id': 'ID',
                        'desc': 'Description',
                        'watchers': []
                    }
                ]
            })
        definitions = self._get_definitions(config)
        self.assertEqual(1, len(definitions))
        definition = definitions[0]
        self.assertEqual('Title', definition.title)
        self.assertEqual('ID', definition.id)
        self.assertEqual('Description', definition.description)
        self.assertEqual([m1, m2], definition.markers)
        self.assertEqual([m1, m2], definition.invalidators)

    def test_multiple_definitions(self):
        m1 = re.compile('a')
        m2 = re.compile('b')
        config = munch.munchify(
            {
                'definitions': [
                    {
                        'markers': [m1],
                        'invalidators': [m1],
                        'title': 'Title1',
                        'id': 'ID1',
                        'desc': 'Description1',
                        'watchers': []
                    }, {
                        'markers': [m2],
                        'invalidators': [m2],
                        'title': 'Title2',
                        'id': 'ID2',
                        'desc': 'Description2',
                        'watchers': []
                    }
                ]
            })
        definitions = self._get_definitions(config)
        self.assertEqual(2, len(definitions))
        self.assertEqual('Title1', definitions[0].title)
        self.assertEqual('Title2', definitions[1].title)
