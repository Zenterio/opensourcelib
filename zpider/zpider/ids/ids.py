import logging

from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from zpider.asciidoctor import GET_ASCIIDOCTOR_OPTIONS
from zpider.commands.html import HTML_COMMAND
from zpider.commands.pdf import PDF_COMMAND
from zpider.commands.yaml import YAML_COMMAND
from zpider.ids import ASCIIDOCTOR_IDS_ENDPOINT, EXCLUDE_IDS, INCLUDE_IDS

logger = logging.getLogger(get_logger_name('zpider', 'ids'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='ids',
    extends=[HTML_COMMAND, PDF_COMMAND, YAML_COMMAND],
    config_options=[
        ConfigOption(EXCLUDE_IDS, required=False),
        ConfigOption(INCLUDE_IDS, required=False),
    ],
    endpoints_and_messages={
        ASCIIDOCTOR_IDS_ENDPOINT: [GET_ASCIIDOCTOR_OPTIONS]
    })
class Ids(AbstractExtension):

    def __init__(self, config, instances):
        self._config = config

    @callback_dispatcher([GET_ASCIIDOCTOR_OPTIONS], [ASCIIDOCTOR_IDS_ENDPOINT])
    def get_document_structure_options(self, message):
        options = []

        include_ids = self._config.get(INCLUDE_IDS, [])
        if include_ids:
            options.extend(
                [
                    '--attribute',
                    'include-ids={include_ids}'.format(include_ids=','.join(include_ids))
                ])

        exclude_ids = self._config.get(EXCLUDE_IDS, [])
        if exclude_ids:
            options.extend(
                [
                    '--attribute',
                    'exclude-ids={exclude_ids}'.format(exclude_ids=','.join(exclude_ids))
                ])

        return ' '.join(options)
