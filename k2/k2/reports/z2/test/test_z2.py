from unittest import TestCase
from unittest.mock import Mock, patch

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from k2.reports.z2 import Z2_INTERNAL_PUBLISH_REPORT_REQUEST, Z2_REPORTS, Z2_REPORTS_BUILD_NUMBER, \
    Z2_REPORTS_ENDPOINT, Z2_REPORTS_FILE, Z2_REPORTS_JOB_NAME, Z2_REPORTS_URL
from k2.reports.z2.z2 import FileReporter, ReportGenerator, UploadReporter
from k2.results import RESULTS_ENDPOINT, TEST_RESULTS_COLLECTED


class TestReportGenerator(TestCase):

    @staticmethod
    def create_harness():
        config = ConfigManager()
        config.set(Z2_REPORTS, True)
        config.set(Z2_REPORTS_JOB_NAME, 'my-job-name')
        config.set(Z2_REPORTS_BUILD_NUMBER, 53)

        harness = ExtensionTestHarness(
            ReportGenerator,
            config=config,
            endpoints_and_messages={
                RESULTS_ENDPOINT: [TEST_RESULTS_COLLECTED],
            })
        return harness

    def test_create_harness(self):
        with self.create_harness():
            pass

    def test_generates_and_publishes_report_when_test_results_are_collected(self):
        with self.create_harness() as harness:
            with harness.message_queue([Z2_INTERNAL_PUBLISH_REPORT_REQUEST], [Z2_REPORTS_ENDPOINT]) as queue, \
                    patch('k2.reports.z2.z2.generate_report') as generate_report:
                report = Mock()
                harness.trigger_event(TEST_RESULTS_COLLECTED, RESULTS_ENDPOINT, data=report)
                queue.get(timeout=5)
                generate_report.assert_called_once_with(report, 'my-job-name', 53)


class TestFileReporter(TestCase):

    @staticmethod
    def create_harness():
        config = ConfigManager()
        config.set(Z2_REPORTS, True)
        config.set(Z2_REPORTS_FILE, 'z2-report.json')

        harness = ExtensionTestHarness(
            FileReporter,
            config=config,
            endpoints_and_messages={
                Z2_REPORTS_ENDPOINT: [Z2_INTERNAL_PUBLISH_REPORT_REQUEST],
            })
        return harness

    def test_create_harness(self):
        with self.create_harness():
            pass

    def test_writes_report_when_publishing_is_requested(self):
        with self.create_harness() as harness, \
                patch('k2.reports.z2.z2.write_report') as write_report:
            report = Mock()
            harness.send_request(Z2_INTERNAL_PUBLISH_REPORT_REQUEST, data=report).wait()
            write_report.assert_called_once_with(report, 'z2-report.json')


class TestUploadReporter(TestCase):

    @staticmethod
    def create_harness():
        config = ConfigManager()
        config.set(Z2_REPORTS, True)
        config.set(Z2_REPORTS_URL, 'http://z2.myawesomedomain.lan')

        harness = ExtensionTestHarness(
            UploadReporter,
            config=config,
            endpoints_and_messages={
                Z2_REPORTS_ENDPOINT: [Z2_INTERNAL_PUBLISH_REPORT_REQUEST],
            })
        return harness

    def test_create_harness(self):
        with self.create_harness():
            pass

    def test_uploads_report_when_publishing_is_requested(self):
        with self.create_harness() as harness, \
                patch('k2.reports.z2.z2.upload_report') as upload_report:
            report = Mock()
            harness.send_request(Z2_INTERNAL_PUBLISH_REPORT_REQUEST, data=report).wait()
            upload_report.assert_called_once_with(report, 'http://z2.myawesomedomain.lan')
