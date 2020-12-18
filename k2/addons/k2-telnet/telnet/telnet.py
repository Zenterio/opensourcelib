"""Provides a telnet component fulfilling the :ref:`exec <exec-label>` interface."""

from zaf.component.decorator import component, requires
from zaf.component.util import add_cans, add_properties
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT, SUT_IP
from telnet import TELNET_ENABLED, TELNET_PORT, TELNET_PROMPT, TELNET_TIMEOUT

from .client import TelnetClient


@requires(context='ComponentContext')
@requires(sut='Sut', can=['telnet'])
@component(name='Exec', can=['telnet'], provided_by_extension='telnet', priority=1)
def telnet_exec(context, sut):
    """
    Exec component using telnet.

    Example:

    .. code-block:: python

        @requires(exec=telnet_exec)
        def get_date_from_sut(exec):
            date = exec.send_line('date', expected_exit_code=0)
            print(date)
    """
    with TelnetClient(sut.ip, sut.telnet.port, sut.telnet.timeout, sut.telnet.prompt,
                      context.callable_qualname) as client:
        yield client


@CommandExtension(
    name='telnet',
    extends=[RUN_COMMAND, 'sut'],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(SUT_IP, required=True),
        ConfigOption(TELNET_ENABLED, required=True),
        ConfigOption(TELNET_PORT, required=False),
        ConfigOption(TELNET_TIMEOUT, required=False),
        ConfigOption(TELNET_PROMPT, required=False)
    ],
    groups=['exec', 'telnet'],
    activate_on=[TELNET_ENABLED],
)
class Telnet(AbstractExtension):
    """Telnet connection."""

    def __init__(self, config, instances):
        self._enabled = config.get(TELNET_ENABLED)
        self._entity = instances.get(SUT)
        self._port = config.get(TELNET_PORT)
        self._timeout = config.get(TELNET_TIMEOUT)
        self._prompt = config.get(TELNET_PROMPT)

    def register_components(self, component_manager):
        if self._enabled is True:
            sut = component_manager.get_unique_class_for_entity(self._entity)
            add_cans(sut, ['telnet'])
            add_properties(
                sut, 'telnet', {
                    'port': self._port,
                    'timeout': self._timeout,
                    'prompt': self._prompt,
                })
