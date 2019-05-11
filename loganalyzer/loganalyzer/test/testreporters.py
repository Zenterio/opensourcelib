"""
Tests the classes in the reporters module.

Note: uses relative imports and hence the parent module need to be loaded.
"""
import unittest
from io import StringIO
from unittest.mock import Mock

from loganalyzer.reporters import WatchersReporter

from ..item import ItemDefinition, ItemInstance, LogData, LogMatch
from ..reporters import ItemStats, ReportingError, TextReporter


class TestTextReporter(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.summary_output = StringIO()
        self.report_output = StringIO()
        self.reporter = TextReporter(self.summary_output, self.report_output)
        mock_match = Mock()
        mock_match.group.return_value = 'Log'
        itemdef1 = ItemDefinition(['a'], [], 'Title1', 'id1', 'desc1')
        itemdef2 = ItemDefinition(['a', 'b'], [], 'Title2', 'id2', 'desc2')
        items = [ItemInstance(itemdef1), ItemInstance(itemdef2), ItemInstance(itemdef1)]
        items[0].set_match(0, LogMatch(LogData(1, 'Log1'), mock_match))
        items[1].set_match(0, LogMatch(LogData(2, 'Log2-a'), mock_match))
        items[1].set_match(1, LogMatch(LogData(4, 'Log2-b'), mock_match))
        items[2].set_match(0, LogMatch(LogData(3, 'Log1'), mock_match))
        self.items = items

    def test_throws_reporting_error_on_failed_write(self):
        mock_stream = Mock()
        mock_stream.write.side_effect = Exception('Induced error')
        r = TextReporter(mock_stream, mock_stream)
        self.assertRaises(ReportingError, r.write_report, self.items)
        self.assertRaises(ReportingError, r.write_summary, self.items)

    def test_summary_lists_count_of_item_type(self):
        self.reporter.write_summary(self.items)

        expected_summary = """SUMMARY:
--------
2 (id1) Title1
1 (id2) Title2
"""
        self.assertEqual(
            expected_summary, self.summary_output.getvalue(), 'Summary did not look as expected')

    def test_report_groups_items_by_definition(self):
        self.reporter.write_report(self.items)
        expected_report = """REPORT:
-------

(id1) Title1
------------
desc1

  1: Log1
     ---

  3: Log1
     ---


(id2) Title2
------------
desc2

  2: Log2-a
     ---
  4: Log2-b
     ---

"""
        self.assertEqual(
            expected_report, self.report_output.getvalue(), 'Report did not look as expected')

    def test_get_headerline(self):
        self.assertEqual('--', self.reporter.get_headerline('aa'))

    def test_get_description_removes_ending_whitespace(self):
        self.assertEqual('desc', self.reporter.get_description('desc\n'))

    def test_no_complete_items_gives_notice_in_summary(self):
        self.reporter.write_summary([])

        expected = """SUMMARY:
--------
Nothing to report
"""
        result = self.summary_output.getvalue()
        self.assertEqual(expected, result)

    def test_no_complete_items_gives_notice_in_report(self):
        self.reporter.write_report([])

        expected = """REPORT:
-------
Nothing to report
"""
        result = self.report_output.getvalue()
        self.assertEqual(expected, result)


class TestItemStatsGetSummaries(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.itemdef1 = ItemDefinition(['a'], 'Title1', 'id1', 'desc1')
        self.itemdef2 = ItemDefinition(['b'], 'Title2', 'id2', 'desc2')
        self.item1a = ItemInstance(self.itemdef1)
        self.item1b = ItemInstance(self.itemdef1)
        self.item2a = ItemInstance(self.itemdef2)
        items = [self.item1a, self.item2a, self.item1b]
        self.item1a.set_match(0, LogMatch(LogData(1, 'Log1'), None))
        self.item1b.set_match(0, LogMatch(LogData(3, 'Log1'), None))
        self.item2a.set_match(0, LogMatch(LogData(2, 'Log2'), None))
        self.summeries = ItemStats().get_item_summaries(items)

    def test_get_summeries(self):
        self.assertEqual(2, len(list(self.summeries)), 'Expected 2 summaries, but was not.')

    def test_sorted_by_definition_id(self):
        ids = [s.definition.definition_id for s in self.summeries]
        sorted_ids = sorted(ids.copy())
        self.assertEqual(sorted_ids, ids, 'Expected sorted, but was not.')

    def test_associated_items_in_list(self):
        items = list(self.summeries)[0].items
        expected = [self.item1a, self.item1b]
        self.assertEqual(expected, items, 'Expected items was not in list')

    def test_no_items_gives_empty_list(self):
        self.assertEqual([], list(ItemStats().get_item_summaries([])))


class TestWatchersReporter(unittest.TestCase):

    def test_no_watchers_does_not_write_to_stream(self):
        super().setUp()
        watchers_file = Mock()
        reporter = WatchersReporter(watchers_file, ', ')
        itemdef1 = ItemDefinition(['a'], [], 'Title1', 'id1', 'desc1', watchers=[])
        itemdef2 = ItemDefinition(['a', 'b'], [], 'Title2', 'id2', 'desc2', watchers=[])
        reporter.write_report([ItemInstance(itemdef1), ItemInstance(itemdef2)])
        watchers_file.write.assert_not_called()

    def test_combines_watchers_from_multiple_items(self):
        super().setUp()
        watchers_file = StringIO()
        reporter = WatchersReporter(watchers_file, ', ')
        itemdef1 = ItemDefinition(['a'], [], 'Title1', 'id1', 'desc1', watchers=['watcher1'])
        itemdef2 = ItemDefinition(['a', 'b'], [], 'Title2', 'id2', 'desc2', watchers=['watcher2'])
        reporter.write_report([ItemInstance(itemdef1), ItemInstance(itemdef2)])
        self.assertEqual(watchers_file.getvalue(), 'watcher1, watcher2')

    def test_remove_duplicate_watchers(self):
        super().setUp()
        watchers_file = StringIO()
        reporter = WatchersReporter(watchers_file, ', ')
        itemdef1 = ItemDefinition(['a'], [], 'Title1', 'id1', 'desc1', watchers=['watcher1'])
        itemdef2 = ItemDefinition(
            ['a', 'b'], [], 'Title2', 'id2', 'desc2', watchers=['watcher2', 'watcher1'])
        reporter.write_report([ItemInstance(itemdef1), ItemInstance(itemdef2)])
        self.assertEqual(watchers_file.getvalue(), 'watcher1, watcher2')
