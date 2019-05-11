from unittest import TestCase
from unittest.mock import MagicMock, Mock

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager

from healthcheck import HEALTH_CHECK_ENDPOINT, PERFORM_HEALTH_CHECK, HealthCheckError
from k2.sut import SUT
from linuxutils.process.pid import HEALTHCHECK_PROC_IDS, HEALTHCHECK_PROC_PATTERNS, \
    SUT_HEALTHCHECK_PROC_IDS

from ..pid import PidMonitorError, ProcMonitoringHealthCheck, ProcPidCollector


class TestProcPidCollector(TestCase):

    def setUp(self):
        self.exec = MagicMock()
        self.collector = ProcPidCollector(self.exec)

    def test_raises_pid_monitor_error_if_exec_raises(self):
        with self.assertRaisesRegex(PidMonitorError, 'Could not collect PID data'):
            self.exec.send_line = MagicMock(side_effect=Exception('/bin/sh: ps: not found'))
            self.collector.collect('abc')

    def test_returns_an_empty_set_if_no_match(self):
        self.exec.send_line = MagicMock(
            return_value=(
                '  PID USER       VSZ STAT COMMAND\n'
                '    1 root      1772 S    init\n'
                '    2 root         0 SW   sleep 10\n'
                '    3 root         0 SW   /bin/false\n'
                '    4 root         0 SW   sleep 10\n'))
        data = self.collector.collect(['nope'])
        self.exec.send_line.assert_called_once_with('ps ww', timeout=5)
        assert data == set()

    def test_returns_an_set_with_matching_pids(self):
        self.exec.send_line = MagicMock(
            return_value=(
                '  PID USER       VSZ STAT COMMAND\n'
                '    1 root      1772 S    init\n'
                '    2 root         0 SW   sleep 10\n'
                '    3 root         0 SW   /bin/false\n'
                '    4 root         0 SW   sleep 10\n'))
        data = self.collector.collect(['sle.*'])
        self.exec.send_line.assert_called_once_with('ps ww', timeout=5)
        assert data == {2, 4}

    def test_multiple_patterns(self):
        self.exec.send_line = MagicMock(
            return_value=(
                '  PID USER       VSZ STAT COMMAND\n'
                '    1 root      1772 S    init\n'
                '    2 root         0 SW   sleep 5\n'
                '    3 root         0 SW   /bin/false\n'
                '    4 root         0 SW   sleep 10\n'))
        data = self.collector.collect(['sle.*', 'false'])
        self.exec.send_line.assert_called_once_with('ps ww', timeout=5)
        assert data == {2, 3, 4}

    def test_negative_patterns(self):
        self.exec.send_line = MagicMock(
            return_value=(
                '  PID USER       VSZ STAT COMMAND\n'
                '    1 root      1772 S    init\n'
                '    2 root         0 SW   sleep 10\n'
                '    3 root         0 SW   /bin/false\n'
                '    4 root         0 SW   sleep 10\n'))
        data = self.collector.collect(['sle.*', '!sleep', 'false'])
        self.exec.send_line.assert_called_once_with('ps ww', timeout=5)
        assert data == {3}


class TestProcMonitoringHealthCheck(TestCase):

    @staticmethod
    def _create_harness():
        config = ConfigManager()
        entity = 'mysut'
        config.set(SUT, [entity])
        config.set(SUT_HEALTHCHECK_PROC_IDS, ['myhealthcheck'], entity=entity)
        config.set(HEALTHCHECK_PROC_IDS, ['myhealthcheck'])
        config.set(HEALTHCHECK_PROC_PATTERNS, ['my_pattern'], entity='myhealthcheck')

        proc_pid_collector = Mock()
        harness = ExtensionTestHarness(
            ProcMonitoringHealthCheck,
            config=config,
            endpoints_and_messages={
                HEALTH_CHECK_ENDPOINT: [PERFORM_HEALTH_CHECK],
            },
            components=[
                ComponentMock(name='ProcPidCollector', mock=proc_pid_collector),
            ])
        harness.proc_pid_collector = proc_pid_collector
        return harness

    def test_does_not_raise_exception_if_pid_is_found(self):
        with self._create_harness() as harness:
            harness.proc_pid_collector.collect.side_effect = [[1]]
            harness.messagebus.send_request(PERFORM_HEALTH_CHECK,
                                            HEALTH_CHECK_ENDPOINT).wait()[0].result()

    def test_raises_exception_if_pid_is_not_found(self):
        with self._create_harness() as harness:
            harness.proc_pid_collector.collect.side_effect = [[]]
            with self.assertRaises(HealthCheckError):
                harness.messagebus.send_request(PERFORM_HEALTH_CHECK,
                                                HEALTH_CHECK_ENDPOINT).wait()[0].result()
