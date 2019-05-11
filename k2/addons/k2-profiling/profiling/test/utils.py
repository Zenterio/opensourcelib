from unittest.mock import Mock

from zaf.application import AFTER_COMMAND, APPLICATION_ENDPOINT, BEFORE_COMMAND
from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager

from .. import PROFILING_CSV, PROFILING_CSV_PATH, PROFILING_DIR, PROFILING_JSON, \
    PROFILING_JSON_PATH, PROFILING_TEXT, PROFILING_TEXT_PATH
from ..profiling import Profiling


def create_harness(
        csv_enabled=True,
        csv_path='path/to/csv/report.csv',
        json_enabled=True,
        json_path='path/to/json/report.json',
        text_enabled=True,
        text_path='path/to/text/report.text'):
    metric_mock = Mock()

    config = ConfigManager()
    config.set(PROFILING_DIR, 'profiling')
    config.set(PROFILING_CSV, csv_enabled)
    config.set(PROFILING_CSV_PATH, csv_path)
    config.set(PROFILING_JSON, json_enabled)
    config.set(PROFILING_JSON_PATH, json_path)
    config.set(PROFILING_TEXT, text_enabled)
    config.set(PROFILING_TEXT_PATH, text_path)

    harness = ExtensionTestHarness(
        Profiling,
        endpoints_and_messages={APPLICATION_ENDPOINT: [BEFORE_COMMAND, AFTER_COMMAND]},
        config=config,
        components=[ComponentMock(name='CreateSingleValueMetric', mock=metric_mock)])
    harness.metrics_mock = metric_mock
    return harness
