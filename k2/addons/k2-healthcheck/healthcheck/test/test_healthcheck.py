from unittest import TestCase
from unittest.mock import Mock

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager
from zaf.messages.dispatchers import CallbackDispatcher, LocalMessageQueue
from zaf.messages.message import EndpointId

from healthcheck import HealthCheckError
from k2.runner import TEST_CASE_FINISHED
from k2.runner.runner import Verdict
from k2.sut import SUT, SUT_RECOVERY_PERFORM

from ..healthcheck import HEALTH_CHECK_ENDPOINT, PERFORM_HEALTH_CHECK, HealthMonitor

MOCK_ENDPOINT = EndpointId('mock endpoint', 'mock description')


class TestHealthMonitor(TestCase):

    @staticmethod
    def create_harness():
        config = ConfigManager()
        config.set(SUT, ['mysut'])

        return ExtensionTestHarness(
            HealthMonitor,
            config=config,
            endpoints_and_messages={
                MOCK_ENDPOINT: [TEST_CASE_FINISHED, SUT_RECOVERY_PERFORM],
            })

    def test_triggers_perform_health_check_on_failed_test(self):
        with TestHealthMonitor.create_harness() as harness:
            with LocalMessageQueue(harness.messagebus, message_ids=[PERFORM_HEALTH_CHECK],
                                   endpoint_ids=[HEALTH_CHECK_ENDPOINT],
                                   entities=['mysut']) as perform_health_check_queue, \
                 LocalMessageQueue(harness.messagebus, message_ids=[SUT_RECOVERY_PERFORM],
                                   endpoint_ids=[MOCK_ENDPOINT],
                                   entities=['mysut']) as sut_recovery_perform_queue:
                data = Mock()
                data.verdict = Verdict.FAILED
                harness.trigger_event(TEST_CASE_FINISHED, MOCK_ENDPOINT, data=data, entity='mysut')
                harness.messagebus.wait_for_not_active()
                assert not perform_health_check_queue.empty()
                assert sut_recovery_perform_queue.empty()

    def test_triggers_perform_health_check_on_errored_test(self):
        with TestHealthMonitor.create_harness() as harness:
            with LocalMessageQueue(harness.messagebus, message_ids=[PERFORM_HEALTH_CHECK],
                                   endpoint_ids=[HEALTH_CHECK_ENDPOINT],
                                   entities=['mysut']) as perform_health_check_queue, \
                 LocalMessageQueue(harness.messagebus, message_ids=[SUT_RECOVERY_PERFORM],
                                   endpoint_ids=[MOCK_ENDPOINT],
                                   entities=['mysut']) as sut_recovery_perform_queue:
                data = Mock()
                data.verdict = Verdict.ERROR
                harness.trigger_event(TEST_CASE_FINISHED, MOCK_ENDPOINT, data=data, entity='mysut')
                harness.messagebus.wait_for_not_active()
                assert not perform_health_check_queue.empty()
                assert sut_recovery_perform_queue.empty()

    def test_does_not_trigger_perform_health_check_on_passed_test(self):
        with TestHealthMonitor.create_harness() as harness:
            with LocalMessageQueue(harness.messagebus, message_ids=[PERFORM_HEALTH_CHECK],
                                   endpoint_ids=[HEALTH_CHECK_ENDPOINT],
                                   entities=['mysut']) as perform_health_check_queue, \
                 LocalMessageQueue(harness.messagebus, message_ids=[SUT_RECOVERY_PERFORM],
                                   endpoint_ids=[MOCK_ENDPOINT],
                                   entities=['mysut']) as sut_recovery_perform_queue:
                data = Mock()
                data.verdict = Verdict.PASSED
                harness.trigger_event(TEST_CASE_FINISHED, MOCK_ENDPOINT, data=data, entity='mysut')
                harness.messagebus.wait_for_not_active()
                assert perform_health_check_queue.empty()
                assert sut_recovery_perform_queue.empty()

    def test_triggers_sut_recovery_perform_on_failed_health_check(self):
        with TestHealthMonitor.create_harness() as harness:

            def handler(message):
                raise HealthCheckError('Nope!')

            dispatcher = CallbackDispatcher(harness.messagebus, handler)
            harness.messagebus.register_dispatcher(
                dispatcher, [PERFORM_HEALTH_CHECK], entities=['mysut'])

            with LocalMessageQueue(harness.messagebus, message_ids=[SUT_RECOVERY_PERFORM],
                                   endpoint_ids=[MOCK_ENDPOINT],
                                   entities=['mysut']) as sut_recovery_perform_queue:
                data = Mock()
                data.verdict = Verdict.FAILED
                harness.trigger_event(TEST_CASE_FINISHED, MOCK_ENDPOINT, data=data, entity='mysut')

                harness.messagebus.wait_for_not_active()
                assert not sut_recovery_perform_queue.empty()

    def test_triggers_sut_recovery_perform_on_errored_health_check(self):
        with TestHealthMonitor.create_harness() as harness:

            def handler(message):
                raise Exception('Could not run health check!')

            dispatcher = CallbackDispatcher(harness.messagebus, handler)
            harness.messagebus.register_dispatcher(
                dispatcher, [PERFORM_HEALTH_CHECK], entities=['mysut'])

            with LocalMessageQueue(harness.messagebus, message_ids=[SUT_RECOVERY_PERFORM],
                                   endpoint_ids=[MOCK_ENDPOINT],
                                   entities=['mysut']) as sut_recovery_perform_queue:
                data = Mock()
                data.verdict = Verdict.FAILED
                harness.trigger_event(TEST_CASE_FINISHED, MOCK_ENDPOINT, data=data, entity='mysut')

                harness.messagebus.wait_for_not_active()
                assert sut_recovery_perform_queue.empty()
