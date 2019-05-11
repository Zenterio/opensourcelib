import unittest

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from zpider.asciidoctor import GET_ASCIIDOCTOR_OPTIONS
from zpider.docstructure import LEVEL_EXCLUDES, LEVEL_INCLUDES, LEVELS_IDS, MAGIC_TITLES
from zpider.docstructure.docstructure import DocStructure


class TestDocStructure(unittest.TestCase):

    def test_magic_titles_attribute_set(self):
        with _create_harness() as harness:
            options = harness.send_request(GET_ASCIIDOCTOR_OPTIONS).wait(timeout=1)[0].result()
            self.assertIn('--attribute magic-titles=m1,m2', options)

    def test_magic_title_attribute_not_included_if_empty(self):
        with _create_empty_config_harness() as harness:
            options = harness.send_request(GET_ASCIIDOCTOR_OPTIONS).wait(timeout=1)[0].result()
            self.assertNotIn('magic-titles', options)

    def test_levels_ids_attribute_set(self):
        with _create_harness() as harness:
            options = harness.send_request(GET_ASCIIDOCTOR_OPTIONS).wait(timeout=1)[0].result()
            self.assertIn('--attribute levels-ids=level,sublevel', options)

    def test_levels_ids_attribute_not_included_if_empty(self):
        with _create_empty_config_harness() as harness:
            options = harness.send_request(GET_ASCIIDOCTOR_OPTIONS).wait(timeout=1)[0].result()
            self.assertNotIn('magic-titles', options)

    def test_levels_includes_attributes_set(self):
        with _create_harness() as harness:
            options = harness.send_request(GET_ASCIIDOCTOR_OPTIONS).wait(timeout=1)[0].result()
            self.assertIn('--attribute levels-level-includes=a,b', options)
            self.assertIn('--attribute levels-sublevel-includes=c,d', options)

    def test_levels_includes_attribute_not_included_if_empty(self):
        with _create_empty_config_harness() as harness:
            options = harness.send_request(GET_ASCIIDOCTOR_OPTIONS).wait(timeout=1)[0].result()
            self.assertNotIn('levels-level-includes', options)
            self.assertNotIn('levels-sublevel-includes', options)

    def test_levels_exludes_attributes_set(self):
        with _create_harness() as harness:
            options = harness.send_request(GET_ASCIIDOCTOR_OPTIONS).wait(timeout=1)[0].result()
            self.assertIn('--attribute levels-level-excludes=e,f', options)
            self.assertIn('--attribute levels-sublevel-excludes=g,h', options)

    def test_levels_excludes_attribute_not_included_if_empty(self):
        with _create_empty_config_harness() as harness:
            options = harness.send_request(GET_ASCIIDOCTOR_OPTIONS).wait(timeout=1)[0].result()
            self.assertNotIn('levels-level-excludes', options)
            self.assertNotIn('levels-sublevel-excludes', options)


def _create_harness():
    config = ConfigManager()
    config.set(LEVELS_IDS, ['level', 'sublevel'])
    config.set(LEVEL_INCLUDES, ['a', 'b'], entity='level')
    config.set(LEVEL_INCLUDES, ['c', 'd'], entity='sublevel')
    config.set(LEVEL_EXCLUDES, ['e', 'f'], entity='level')
    config.set(LEVEL_EXCLUDES, ['g', 'h'], entity='sublevel')
    config.set(MAGIC_TITLES, ['m1', 'm2'])
    return ExtensionTestHarness(DocStructure, config=config)


def _create_empty_config_harness(levels=['level', 'sublevel']):
    config = ConfigManager()
    config.set(LEVELS_IDS, levels)

    return ExtensionTestHarness(DocStructure, config=config)
