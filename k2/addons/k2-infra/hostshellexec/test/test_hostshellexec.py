from unittest import TestCase

from zaf.builtin.unittest.harness import ExtensionTestHarness
from zaf.config.manager import ConfigManager

from ..hostshellexec import HOST_SHELL_EXEC_ENABLED, HOST_SHELL_EXEC_ENCODING, \
    HOST_SHELL_EXEC_TIMEOUT, HostShellExec


class TestHostShellExec(TestCase):

    @staticmethod
    def create_harness(enabled=True):
        config = ConfigManager()
        config.set(HOST_SHELL_EXEC_ENABLED, enabled)
        config.set(HOST_SHELL_EXEC_TIMEOUT, 120)
        config.set(HOST_SHELL_EXEC_ENCODING, 'ascii')
        return ExtensionTestHarness(HostShellExec, config=config)

    def test_configuration(self):
        with TestHostShellExec.create_harness() as harness:
            assert harness.extension._enabled is True
            assert harness.extension._timeout == 120
            assert harness.extension._encoding == 'ascii'

    def test_registers_a_host_exec_component_if_enabled(self):
        with TestHostShellExec.create_harness() as harness:
            assert 'Exec' in harness.component_registry

    def test_does_not_register_a_host_exec_component_if_disabled(self):
        with TestHostShellExec.create_harness(enabled=False) as harness:
            assert 'Exec' not in harness.component_registry
