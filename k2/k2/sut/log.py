"""
Helper classes and functions for working with SUT log sources.

Extensions who wish to announce that they provide a source of SUT log lines have to populated the
:ref:`option-suts.<ids>.log.sources` config option. The easiest way to do this is by defining a
FrameworkExtension and implementing the get_config member, like so:

.. code-block:: python

    @FrameworkExtension(name='zserial', load_order=91, groups=['log_sources', 'serial'])
    class SerialFrameworkExtension(AbstractExtension):
        def get_config(self, config, requested_config_options, requested_command_config_options):
            log_config = dict()
            for sut in config.get(SUT):
                if config.get(SERIAL_ENABLED, entity=sut) and config.get(SERIAL_LOG_ENABLED,
                                                                         entity=sut):
                    sut_add_log_source(log_config, sut, serial_log_line_entity(sut))
            return ExtensionConfig(log_config, 1, 'zserial')

This extension would then post LOG_LINE_RECEIVED events to serial log entities it announced. Please
note that the load_order in the above example has to be at least 91, so that any command line
parameters have been successfully parsed. See the "Framework Extensions::Load Order" section in the
dev guide for more details.

This config option can be used by extensions who wish to react or process log lines coming from a
sut. The extension would have to listen to LOG_LINE_RECEIVED events for the available log line
sources, or a subset of them.
"""

from zaf.application import ApplicationContext
from zaf.config.options import ConfigOptionId

from . import SUT

SUT_LOG_SOURCES = ConfigOptionId(
    'log.sources',
    """\
    List of sources which can provide log lines from the sut.

    Extensions which can trigger LOG_LINE_RECEIVED events will automatically extend this list.
    """,
    at=SUT,
    option_type=str,
    multiple=True,
    hidden=True,
    application_contexts=ApplicationContext.INTERNAL)


class NoLogSources(Exception):
    pass


def sut_add_log_source(config, sut, source):
    log_sources = '.'.join([SUT.namespace, sut, SUT_LOG_SOURCES.name])
    try:
        config[log_sources].append(source)
    except KeyError:
        config[log_sources] = [source]
