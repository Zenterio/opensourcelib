import unittest
from threading import Event, Lock
from unittest.mock import MagicMock, Mock, call

from zaf.builtin.unittest.harness import ComponentMock, ExtensionTestHarness
from zaf.config.manager import ConfigManager

from k2.cmd.run import INITIALIZE_SUT, POST_INITIALIZE_SUT, RUN_COMMAND_ENDPOINT
from k2.sut import SUT
from orchestration.ansible import ANSIBLE_PARALLEL_RUNS, SUT_ANSIBLE_TEST_NODE
from orchestration.ansible.initialize import INITIALIZE_ANSIBLE_NODE, \
    INITIALIZE_ANSIBLE_SUTS_ENDPOINT, InitializeAnsibleSuts


class TestInitializeAnsibleSuts(unittest.TestCase):

    def test_dispatchers_registered_when_extension_is_active(self):
        with create_harness() as h:
            self.assertTrue(
                h.messagebus.has_registered_dispatchers(
                    INITIALIZE_ANSIBLE_NODE, INITIALIZE_ANSIBLE_SUTS_ENDPOINT, 'sut1'))
            self.assertTrue(
                h.messagebus.has_registered_dispatchers(
                    INITIALIZE_ANSIBLE_NODE, INITIALIZE_ANSIBLE_SUTS_ENDPOINT, 'sut2'))

    def test_dispatchers_registered_only_for_ansible_nodes(self):
        with create_harness(ansible_nodes=['sut2']) as h:
            self.assertFalse(
                h.messagebus.has_registered_dispatchers(
                    INITIALIZE_ANSIBLE_NODE, INITIALIZE_ANSIBLE_SUTS_ENDPOINT, 'sut1'))
            self.assertTrue(
                h.messagebus.has_registered_dispatchers(
                    INITIALIZE_ANSIBLE_NODE, INITIALIZE_ANSIBLE_SUTS_ENDPOINT, 'sut2'))

    def test_suts_initialized_in_parallel_when_enough_parallel_workers(self):
        ansible_node_mock = MagicMock()

        lock = Lock()
        first = Event()
        second = Event()

        def enter():
            with lock:
                if not first.is_set():
                    set = first
                    wait = second
                else:
                    set = second
                    wait = first

                set.set()

            assert wait.wait(timeout=1), 'Enter timed out'

        ansible_node_mock.__enter__.side_effect = enter

        with create_harness(ansible_node_mock=ansible_node_mock) as h:
            h.messagebus.trigger_event(INITIALIZE_SUT, RUN_COMMAND_ENDPOINT, entity='sut1')
            h.messagebus.trigger_event(INITIALIZE_SUT, RUN_COMMAND_ENDPOINT, entity='sut2')

            h.messagebus.trigger_event(POST_INITIALIZE_SUT, RUN_COMMAND_ENDPOINT, entity='sut2')
            h.messagebus.trigger_event(POST_INITIALIZE_SUT, RUN_COMMAND_ENDPOINT, entity='sut1')

            ansible_node_mock.__exit__.assert_has_calls(
                [call(None, None, None), call(None, None, None)])


def create_harness(
        parallel_runs=2,
        suts=('sut1', 'sut2'),
        ansible_nodes=('sut1', 'sut2'),
        ansible_node_mock=Mock()):
    config = ConfigManager()
    config.set(ANSIBLE_PARALLEL_RUNS, parallel_runs)
    config.set(SUT, suts)
    for node in ansible_nodes:
        config.set(SUT_ANSIBLE_TEST_NODE, True, entity=node)

    return ExtensionTestHarness(
        InitializeAnsibleSuts,
        endpoints_and_messages={RUN_COMMAND_ENDPOINT: [INITIALIZE_SUT, POST_INITIALIZE_SUT]},
        config=config,
        components=[ComponentMock(name='AnsibleNode', mock=ansible_node_mock)],
    )
