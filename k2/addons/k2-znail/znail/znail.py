"""
Interact with Znail devices.

For more information, please see:
https://github.com/znailnetem/znail
"""

import logging

from zaf.component.decorator import component, requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT

from . import ZNAIL_IP, ZNAIL_PORT, ZNAIL_TIMEOUT
from .component import ZnailComponent

logger = logging.getLogger(get_logger_name('k2', 'znail'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='znail',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(SUT, required=False, instantiate_on=True),
        ConfigOption(ZNAIL_IP, required=False),
        ConfigOption(ZNAIL_PORT, required=True),
        ConfigOption(ZNAIL_TIMEOUT, required=True),
    ],
    endpoints_and_messages={})
class Znail(AbstractExtension):

    def __init__(self, config, instances):
        self._entity = config.get(SUT)
        self._ip = config.get(ZNAIL_IP, None)
        self._port = config.get(ZNAIL_PORT)
        self._timeout = config.get(ZNAIL_TIMEOUT)

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def timeout(self):
        return self._timeout

    def register_components(self, component_manager):

        @requires(sut='Sut', can=[self._entity])
        class ZnailComponentInstance(ZnailComponent):

            def __init__(self, sut):
                pass

        if self._ip:
            component(name='Znail')(ZnailComponentInstance, component_manager)
            ZnailComponentInstance.ip = self.ip
            ZnailComponentInstance.port = self.port
            ZnailComponentInstance.timeout = self.timeout
