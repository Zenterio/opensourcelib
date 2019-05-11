"""Extension providing the default logging configuration and the :ref:`option-verbose` option."""
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, ExtensionConfig, FrameworkExtension

from zebra.logging import VERBOSE


@FrameworkExtension(
    'zebralogging', load_order=29, config_options=[ConfigOption(VERBOSE, required=True)])
class ZebraLoggingExtension(AbstractExtension):

    def get_config(self, config, requested_config_options, requested_command_config_options):
        verbosity = config.get(VERBOSE)

        if verbosity == 0:
            return ExtensionConfig(
                {
                    'log.warning': [''],
                    'log.info': ['zebra'],
                    'log.debug': [],
                },
                9,
                source='verbosity')
        else:
            return ExtensionConfig(
                {
                    'log.warning': [''],
                    'log.info': [],
                    'log.debug': ['zebra'],
                },
                9,
                source='verbosity')
