"""
Tests the classes in the application module.

Note: uses relative imports and hence the parent module need to be loaded.
"""
import unittest
from unittest.mock import Mock, call

from ..application import LogAnalyzerApplication


class TestApplication(unittest.TestCase):

    def test_application_execution_flow(self):
        data = ['a', 'b']
        items = [1, 2]
        analyzer = Mock()
        analyzer.get_items.return_value = items
        datasource = Mock()
        datasource.get_data.return_value = data
        reporter = Mock()

        app = LogAnalyzerApplication(analyzer, datasource, reporter)
        app.run()

        datasource.get_data.assert_called_with()
        analyzer.analyze.assert_has_calls([call(d) for d in data])
        reporter.write_summary.assert_called_once_with(items)
        reporter.write_report.assert_called_once_with(items)
