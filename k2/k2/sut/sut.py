"""
Provides the Sut (System under test) instances and components enabling instance specific configuration.

The :ref:`suts.ids <option-suts.ids>` config option provided by this extension can be used to
instantiate one or multiple suts.
"""
import logging

from zaf.component.decorator import component
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT, SUT_ADD_CANS, SUT_IP, SUT_RESET_DONE_TIMEOUT, SUT_RESET_STARTED_TIMEOUT

logger = logging.getLogger(get_logger_name('k2', 'sut'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='sut',
    extends=[RUN_COMMAND, 'sut'],
    config_options=[
        ConfigOption(SUT, required=True, instantiate_on=True),
        ConfigOption(SUT_IP, required=False),
        ConfigOption(SUT_ADD_CANS, required=False),
        ConfigOption(SUT_RESET_STARTED_TIMEOUT, required=False),
        ConfigOption(SUT_RESET_DONE_TIMEOUT, required=False),
    ])
class Sut(AbstractExtension):
    """Creates a Sut component."""

    def __init__(self, config, instances):
        self._entity = instances[SUT]
        self._ip = config.get(SUT_IP)
        self._add_cans = config.get(SUT_ADD_CANS)
        self._reset_started_timeout = config.get(SUT_RESET_STARTED_TIMEOUT)
        self._reset_done_timeout = config.get(SUT_RESET_DONE_TIMEOUT)

    def register_components(self, component_manager):
        logger.debug("Registering sut with ip '{ip}'".format(ip=self._ip))
        sut = component_manager.get_unique_class_for_entity(self._entity)
        sut.ip = self._ip
        sut.reset_started_timeout = self._reset_started_timeout
        sut.reset_done_timeout = self._reset_done_timeout

        cans = set(self._add_cans)
        cans.add(self._entity)
        component(name='Sut', scope='session', can=cans)(sut)
