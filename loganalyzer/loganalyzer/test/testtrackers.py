"""
Tests the classes in the trackers module.

Note: uses relative imports and hence the parent module need to be loaded.
"""
import re
import unittest

from ..item import Collector, ItemDefinition, LogData
from ..trackers import SingleTracker


class TestSingleTrackerOneDefinitionOneMarker(unittest.TestCase):

    def setUp(self):
        super().setUp()
        markers = [re.compile('MARKER')]
        definitions = [ItemDefinition(markers, [])]
        self.collector = Collector()
        self.tracker = SingleTracker(definitions)
        self.data = LogData(1, 'text directly before MARKER and after')

    def test_no_instance_added_to_collector_on_no_complete_match(self):
        self.tracker.analyze(LogData(1, 'no matching text'), self.collector)
        self.assertEqual(len(self.collector), 0, 'Length of collector was not 0 as expected.')

    def test_one_instance_added_to_collector_on_one_full_match(self):
        self.tracker.analyze(self.data, self.collector)
        self.assertEqual(len(self.collector), 1, 'Length of collector was not 1 as expected.')
        item = self.collector[0]
        self.assertEqual(
            item.matches[0].data, self.data, 'Collector had not collected item with expected data.')

    def test_multiple_instances_added_to_collector_on_multiple_complete_matches(self):
        self.tracker.analyze(self.data, self.collector)
        self.tracker.analyze(self.data, self.collector)
        self.assertEqual(len(self.collector), 2, 'Length of collector was not 2 as expected.')
        for item in self.collector:
            self.assertEqual(
                item.matches[0].data, self.data,
                'Collector had not collected item with expected data.')


class TestSingleTrackerOneDefinitionMultipleMarkers(unittest.TestCase):

    def setUp(self):
        super().setUp()
        markers = [re.compile('FIRST'), re.compile('SECOND')]
        definitions = [ItemDefinition(markers, [])]
        self.collector = Collector()
        self.tracker = SingleTracker(definitions)
        self.data1 = LogData(1, 'data with FIRST marker')
        self.data2 = LogData(2, 'data with SECOND marker')

    def test_no_instance_added_to_collector_on_incomplete_match(self):
        self.tracker.analyze(self.data2, self.collector)
        self.assertEqual(len(self.collector), 0, 'Length of collector was not 0 as expected.')

    def test_one_instance_added_to_collector_on_one_complete_match(self):
        self.tracker.analyze(self.data1, self.collector)
        self.tracker.analyze(self.data2, self.collector)
        self.assertEqual(len(self.collector), 1, 'Length of collector was not 1 as expected.')
        item = self.collector[0]
        self.assertEqual(
            item.matches[0].data, self.data1,
            'Collector had not collected item with expected data for first match.')
        self.assertEqual(
            item.matches[1].data, self.data2,
            'Collector had not collected item with expected data for second match.')

    def test_newer_match_overwrite_existing_match(self):
        new_data = LogData(3, 'New data with FIRST marker')

        self.tracker.analyze(self.data1, self.collector)
        self.tracker.analyze(new_data, self.collector)
        self.tracker.analyze(self.data2, self.collector)
        self.assertEqual(len(self.collector), 1, 'Length of collector was not 1 as expected.')
        item = self.collector[0]
        self.assertEqual(
            item.matches[0].data, new_data,
            'Collector had not collected item with expected data for first match.')
        self.assertEqual(
            item.matches[1].data, self.data2,
            'Collector had not collected item with expected data for second match.')


class TestSingleTrackerMultipleDefinitions(unittest.TestCase):

    def setUp(self):
        super().setUp()
        markers = [re.compile('FIRST'), re.compile('SECOND')]
        definition1 = ItemDefinition(markers, [])
        definition2 = ItemDefinition([re.compile('MARKER')], [])
        definitions = [definition1, definition2]
        self.collector = Collector()
        self.tracker = SingleTracker(definitions)

        self.data1 = LogData(1, 'data with FIRST marker')
        self.data2 = LogData(2, 'data with SECOND marker')
        self.data3 = LogData(3, 'text directly before MARKER and after')

    def test_no_instance_added_to_collector_on_incomplete_match(self):
        self.tracker.analyze(self.data2, self.collector)
        self.assertEqual(len(self.collector), 0, 'Length of collector was not 0 as expected.')

    def test_instances_added_to_collector_on_complete_match(self):
        self.tracker.analyze(self.data1, self.collector)
        self.tracker.analyze(self.data2, self.collector)
        self.assertEqual(len(self.collector), 1, 'Length of collector was not 1 as expected.')
        self.tracker.analyze(self.data3, self.collector)
        self.assertEqual(len(self.collector), 2, 'Length of collector was not 2 as expected.')
        item = self.collector[0]
        self.assertEqual(
            item.matches[0].data, self.data1,
            'Collector had not collected item with expected data for first match.')
        self.assertEqual(
            item.matches[1].data, self.data2,
            'Collector had not collected item with expected data for second match.')
        item = self.collector[1]
        self.assertEqual(
            item.matches[0].data, self.data3,
            'Collector had not collected item with expected data for marker match.')


class TestSingleTrackerSingleInvalidator(unittest.TestCase):

    def setUp(self):
        super().setUp()
        m1 = re.compile('FIRST')
        m2 = re.compile('SECOND')
        m3 = re.compile('THIRD')
        m_inv = re.compile('INVALID')
        definition1 = ItemDefinition([m1, m2], [m_inv])
        definition2 = ItemDefinition([m1, m2, m3], [m3, m_inv])
        definitions = [definition1, definition2]
        self.collector = Collector()
        self.tracker = SingleTracker(definitions)

        self.data1 = LogData(1, 'data with FIRST marker')
        self.data2 = LogData(2, 'INVALID')
        self.data3 = LogData(3, 'data with SECOND marker')
        self.data4 = LogData(4, 'data with THIRD marker')

    def test_instance_not_added_to_collector_if_invalidated(self):
        self.tracker.analyze(self.data1, self.collector)
        self.tracker.analyze(self.data2, self.collector)
        self.tracker.analyze(self.data3, self.collector)
        self.assertEqual(len(self.collector), 0, 'Length of collector was not 0 as expected.')

    def test_invalidate_has_higher_prio_than_markers_if_completed_by_same_data(self):
        self.tracker.analyze(self.data1, self.collector)
        self.tracker.analyze(self.data2, self.collector)
        self.tracker.analyze(self.data3, self.collector)
        self.tracker.analyze(self.data4, self.collector)
        self.assertEqual(len(self.collector), 0, 'Length of collector was not 0 as expected.')
