import logging

from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from zpider.asciidoctor import GET_ASCIIDOCTOR_OPTIONS
from zpider.commands.html import HTML_COMMAND
from zpider.commands.pdf import PDF_COMMAND
from zpider.commands.yaml import YAML_COMMAND
from zpider.docstructure import ASCIIDOCTOR_DOCSTRUCTURE_ENDPOINT, KEEP_ALL_VERSIONS, \
    KEEP_EMPTY_SECTIONS, LEVEL_EXCLUDES, LEVEL_INCLUDES, LEVELS_IDS, MAGIC_TITLES, \
    MAX_ALLOWED_VERSION

logger = logging.getLogger(get_logger_name('zpider', 'docstructure'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='plugins',
    extends=[HTML_COMMAND, PDF_COMMAND, YAML_COMMAND],
    config_options=[
        ConfigOption(LEVELS_IDS, required=False),
        ConfigOption(LEVEL_INCLUDES, required=False),
        ConfigOption(LEVEL_EXCLUDES, required=False),
        ConfigOption(MAGIC_TITLES, required=False),
        ConfigOption(KEEP_EMPTY_SECTIONS, required=True),
        ConfigOption(MAX_ALLOWED_VERSION, required=False),
        ConfigOption(KEEP_ALL_VERSIONS, required=True)
    ],
    endpoints_and_messages={
        ASCIIDOCTOR_DOCSTRUCTURE_ENDPOINT: [GET_ASCIIDOCTOR_OPTIONS],
    },
)
class DocStructure(AbstractExtension):

    def __init__(self, config, instances):
        self._config = config

    @callback_dispatcher([GET_ASCIIDOCTOR_OPTIONS], [ASCIIDOCTOR_DOCSTRUCTURE_ENDPOINT])
    def get_document_structure_options(self, message):
        options = []

        levels = self._config.get(LEVELS_IDS, [])
        options.extend(['--attribute', 'levels-ids={levels}'.format(levels=','.join(levels))])
        for level in levels:
            includes = self._config.get(LEVEL_INCLUDES, [], entity=level)
            if includes:
                options.extend(
                    [
                        '--attribute', 'levels-{level}-includes={includes}'.format(
                            level=level, includes=','.join(includes))
                    ])

            excludes = self._config.get(LEVEL_EXCLUDES, [], entity=level)
            if excludes:
                options.extend(
                    [
                        '--attribute', 'levels-{level}-excludes={excludes}'.format(
                            level=level, excludes=','.join(excludes))
                    ])

        magic_titles = self._config.get(MAGIC_TITLES, [])
        if magic_titles:
            options.extend(
                [
                    '--attribute',
                    'magic-titles={magic_titles}'.format(magic_titles=','.join(magic_titles))
                ])

        if self._config.get(KEEP_EMPTY_SECTIONS):
            options.extend(['--attribute', 'keep-empty-sections'])

        max_allowed_version = self._config.get(MAX_ALLOWED_VERSION, False)
        if max_allowed_version:
            options.extend(
                [
                    '--attribute', 'max-allowed-version={max_allowed_version}'.format(
                        max_allowed_version=max_allowed_version)
                ])

        if self._config.get(KEEP_ALL_VERSIONS):
            options.extend(['--attribute', 'keep-all-versions'])

        return ' '.join(options)
