import logging
import os

from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from zpider.asciidoctor import ASCIIDOCTOR_PLUGINS_ENDPOINT, GET_ASCIIDOCTOR_OPTIONS, PLUGIN_DIRS
from zpider.commands.html import HTML_COMMAND
from zpider.commands.pdf import PDF_COMMAND
from zpider.commands.yaml import YAML_COMMAND
from zpider.data import data_file

logger = logging.getLogger(get_logger_name('zpider', 'asciidoctor'))
logger.addHandler(logging.NullHandler())

INTERNAL_PLUGIN_DIRECTORY = data_file('plugins')
STANDARD_PLUGINS = ['asciidoctor-diagram']


@CommandExtension(
    name='plugins',
    extends=[HTML_COMMAND, PDF_COMMAND, YAML_COMMAND],
    config_options=[
        ConfigOption(PLUGIN_DIRS, required=False),
    ],
    endpoints_and_messages={
        ASCIIDOCTOR_PLUGINS_ENDPOINT: [GET_ASCIIDOCTOR_OPTIONS],
    },
)
class AsciidoctorPlugins(AbstractExtension):

    def __init__(self, config, instances):
        self._plugins_dirs = config.get(PLUGIN_DIRS)

    @callback_dispatcher([GET_ASCIIDOCTOR_OPTIONS], [ASCIIDOCTOR_PLUGINS_ENDPOINT])
    def get_plugins(self, message):
        plugins = []
        for plugin_dir in list(self._plugins_dirs) + [INTERNAL_PLUGIN_DIRECTORY]:
            for plugin in [file for file in os.listdir(plugin_dir) if file.endswith('.rb')]:
                plugins.append(os.path.join(plugin_dir, plugin))

        plugins.extend(STANDARD_PLUGINS)

        plugin_options = []
        for plugin in plugins:
            plugin_options.extend(['-r', plugin])
        return ' '.join(plugin_options)
