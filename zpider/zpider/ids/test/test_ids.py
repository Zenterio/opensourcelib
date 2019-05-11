import unittest

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from zpider.asciidoctor import GET_ASCIIDOCTOR_OPTIONS
from zpider.ids import EXCLUDE_IDS, INCLUDE_IDS
from zpider.ids.ids import Ids


class TestIds(unittest.TestCase):

    def test_no_id_configured_no_attribute_set(self):
        with _create_harness() as harness:
            options = harness.send_request(GET_ASCIIDOCTOR_OPTIONS).wait(timeout=1)[0].result()
            self.assertEqual('', options)

    def test_include_id_configured_attribute_set(self):
        with _create_harness(include_ids=['1']) as harness:
            options = harness.send_request(GET_ASCIIDOCTOR_OPTIONS).wait(timeout=1)[0].result()
            self.assertIn('--attribute include-ids=1', options)

    def test_include_many_ids_configured_attribute_list_set(self):
        with _create_harness(include_ids=['1', '2']) as harness:
            options = harness.send_request(GET_ASCIIDOCTOR_OPTIONS).wait(timeout=1)[0].result()
            self.assertIn('--attribute include-ids=1,2', options)

    def test_exclude_id_configured_attribute_set(self):
        with _create_harness(exclude_ids=['1']) as harness:
            options = harness.send_request(GET_ASCIIDOCTOR_OPTIONS).wait(timeout=1)[0].result()
            self.assertIn('--attribute exclude-ids=1', options)

    def test_exclude_many_ids_configured_attribute_list_set(self):
        with _create_harness(exclude_ids=['1', '2']) as harness:
            options = harness.send_request(GET_ASCIIDOCTOR_OPTIONS).wait(timeout=1)[0].result()
            self.assertIn('--attribute exclude-ids=1,2', options)


def _create_harness(include_ids=[], exclude_ids=[]):
    config = ConfigManager()
    config.set(INCLUDE_IDS, include_ids)
    config.set(EXCLUDE_IDS, exclude_ids)

    return ExtensionTestHarness(Ids, config=config)
