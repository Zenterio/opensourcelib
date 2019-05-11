from queue import Empty
from unittest import TestCase

from zaf.messages.dispatchers import LocalMessageQueue

from k2.cmd.run import POST_INITIALIZE_SUT, RUN_COMMAND_ENDPOINT
from k2.sut import SUT_RECOVERY_PERFORM

from .. import CONNECTIONCHECK_ENDPOINT, CONNECTIONCHECK_RUN_CHECKS
from .utils import MockConnectionCheck, create_harness


class TestSerialExtension(TestCase):

    def test_extension_registers_dispatchers(self):
        with create_harness() as harness:
            assert harness.messagebus.has_registered_dispatchers(
                POST_INITIALIZE_SUT, RUN_COMMAND_ENDPOINT, 'entity')
            assert harness.messagebus.has_registered_dispatchers(
                CONNECTIONCHECK_RUN_CHECKS, CONNECTIONCHECK_ENDPOINT, 'entity')

    def test_extension_pre_inialize_sut_forwards_request_to_run_all_checks_that_triggers_individual_check(
            self):
        with create_harness() as harness:
            with MockConnectionCheck(harness.messagebus, success=True, required=True,
                                     entity='entity') as mockcc:
                harness.messagebus.trigger_event(
                    POST_INITIALIZE_SUT, RUN_COMMAND_ENDPOINT, 'entity')
                assert mockcc.executed

    def test_extension_run_all_checks_triggers_recovery_when_specified_and_required_check_fails(
            self):
        with create_harness() as harness:
            with LocalMessageQueue(harness.messagebus, [SUT_RECOVERY_PERFORM],
                                   entities=['entity']) as queue:
                with MockConnectionCheck(harness.messagebus, success=False, required=True,
                                         entity='entity'):
                    trigger_recover = True
                    harness.messagebus.send_request(
                        CONNECTIONCHECK_RUN_CHECKS,
                        CONNECTIONCHECK_ENDPOINT,
                        entity='entity',
                        data=trigger_recover)

                    assert queue.get(timeout=1).message_id == SUT_RECOVERY_PERFORM

    def test_extension_run_all_checks_triggers_recovery_when_one_of_multiple_required_checks_fails(
            self):
        with create_harness() as harness:
            with LocalMessageQueue(harness.messagebus, [SUT_RECOVERY_PERFORM],
                                   entities=['entity']) as queue:
                with MockConnectionCheck(harness.messagebus, success=True, required=True, entity='entity'), \
                        MockConnectionCheck(harness.messagebus, success=False, required=True, entity='entity'), \
                        MockConnectionCheck(harness.messagebus, success=True, required=True, entity='entity'):
                    harness.messagebus.send_request(
                        POST_INITIALIZE_SUT, RUN_COMMAND_ENDPOINT, entity='entity')

                    assert queue.get(timeout=1).message_id == SUT_RECOVERY_PERFORM

    def test_extension_run_all_checks_does_not_trigger_recovery_if_not_configured_to_do_so(self):
        with create_harness(should_recover=False) as harness:
            with LocalMessageQueue(harness.messagebus, [SUT_RECOVERY_PERFORM],
                                   entities=['entity']) as queue:
                with MockConnectionCheck(harness.messagebus, success=True, required=True, entity='entity'), \
                        MockConnectionCheck(harness.messagebus, success=False, required=True, entity='entity'), \
                        MockConnectionCheck(harness.messagebus, success=True, required=True, entity='entity'):
                    harness.messagebus.send_request(
                        POST_INITIALIZE_SUT, RUN_COMMAND_ENDPOINT, entity='entity').wait(timeout=1)

                    self.assertRaises(Empty, queue.get_nowait)

    def test_extension_run_all_checks_does_not_trigger_recovery_when_not_specified(self):
        with create_harness() as harness:
            with LocalMessageQueue(harness.messagebus, [SUT_RECOVERY_PERFORM],
                                   entities=['entity']) as queue:
                with MockConnectionCheck(harness.messagebus, success=False, required=True,
                                         entity='entity'):
                    harness.messagebus.send_request(
                        CONNECTIONCHECK_RUN_CHECKS,
                        CONNECTIONCHECK_ENDPOINT,
                        entity='entity',
                        data=False).wait(timeout=1)

                    self.assertRaises(Empty, queue.get_nowait)

    def test_extension_run_all_checks_does_not_trigger_recovery_when_not_required_check_fails(self):
        with create_harness() as harness:
            with LocalMessageQueue(harness.messagebus, [SUT_RECOVERY_PERFORM],
                                   entities=['entity']) as queue:
                with MockConnectionCheck(harness.messagebus, success=False, required=False,
                                         entity='entity'):
                    harness.messagebus.send_request(
                        CONNECTIONCHECK_RUN_CHECKS,
                        CONNECTIONCHECK_ENDPOINT,
                        entity='entity',
                        data=True).wait(timeout=1)

                    self.assertRaises(Empty, queue.get_nowait)

    def test_extension_run_all_checks_does_not_triggers_recovery_when_only_not_required_check_fails(
            self):
        with create_harness() as harness:
            with LocalMessageQueue(harness.messagebus, [SUT_RECOVERY_PERFORM],
                                   entities=['entity']) as queue:
                with MockConnectionCheck(harness.messagebus, success=True, required=True, entity='entity'), \
                        MockConnectionCheck(harness.messagebus, success=False, required=False, entity='entity'), \
                        MockConnectionCheck(harness.messagebus, success=True, required=True, entity='entity'):
                    harness.messagebus.send_request(
                        CONNECTIONCHECK_RUN_CHECKS,
                        CONNECTIONCHECK_ENDPOINT,
                        entity='entity',
                        data=False).wait(timeout=1)

                    self.assertRaises(Empty, queue.get_nowait)

    def test_extension_no_checks_registered_for_entity(self):
        with create_harness() as harness:
            with MockConnectionCheck(harness.messagebus, success=True, required=True,
                                     entity='entity2'):
                harness.messagebus.send_request(
                    CONNECTIONCHECK_RUN_CHECKS,
                    CONNECTIONCHECK_ENDPOINT,
                    entity='entity',
                    data=False).wait(timeout=1)[0].result(timeout=0)
