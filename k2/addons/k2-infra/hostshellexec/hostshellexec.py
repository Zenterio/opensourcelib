"""Run arbitrary shell commands on the host running K2."""

from zaf.component.decorator import component
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension

from k2.cmd.run import RUN_COMMAND

from . import HOST_SHELL_EXEC_ENABLED, HOST_SHELL_EXEC_ENCODING, HOST_SHELL_EXEC_TIMEOUT
from .executor import HostShellExecutor


@CommandExtension(
    name='hostshellexec',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(HOST_SHELL_EXEC_ENABLED, required=True),
        ConfigOption(HOST_SHELL_EXEC_TIMEOUT, required=True),
        ConfigOption(HOST_SHELL_EXEC_ENCODING, required=True),
    ],
    endpoints_and_messages={})
class HostShellExec(AbstractExtension):
    """Provides an Exec component for running shell commands on the host running K2."""

    def __init__(self, config, instances):
        self._enabled = config.get(HOST_SHELL_EXEC_ENABLED)
        self._timeout = config.get(HOST_SHELL_EXEC_TIMEOUT)
        self._encoding = config.get(HOST_SHELL_EXEC_ENCODING)

    def register_components(self, component_manager):
        if self._enabled:
            self._register_host_exec_component(component_manager)

    def _register_host_exec_component(self, component_manager):

        def host_exec():
            return HostShellExecutor(self._timeout, self._encoding)

        register_component = component(name='Exec', can=['host'])
        register_component(host_exec, component_manager)
