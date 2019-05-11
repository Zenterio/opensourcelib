from zaf.config.options import ConfigOptionId
from zaf.config.types import Path
from zaf.messages.message import EndpointId, MessageId


class GenerateDocException(Exception):
    pass


ADOC_FILE = ConfigOptionId(
    'adoc.file', 'The input Asciidoctor file', option_type=Path(exists=True), argument=True)
PLUGIN_DIRS = ConfigOptionId(
    'plugin.dirs',
    'Directories with Asciidoctor plugins. Can be provided multiple times.',
    multiple=True,
    option_type=Path(exists=True))

ASCIIDOCTOR_ENDPOINT = EndpointId('ASCIIDOCTOR_ENDPOINT', 'Endpoint for Asciidoctor Extension')
ASCIIDOCTOR_PLUGINS_ENDPOINT = EndpointId(
    'ASCIIDOCTOR_PLUGINS_ENDPOINT', 'Endpoint that handles Asciidoctor Plugins')

GENERATE_DOC = MessageId(
    'GENERATE_DOC', """
    Request to generate documentation

    data: AsciidoctorCommand object
    """)

GET_ASCIIDOCTOR_OPTIONS = MessageId(
    'GET_ASCIIDOCTOR_OPTIONS', """
    Get command line options for the Asciidoctor command

    data: String with preformated options
    """)


class AsciidoctorCommand(object):

    def __init__(self, output_path):
        self._output_path = output_path

    @property
    def command(self):
        return 'asciidoctor'

    @property
    def output_path(self):
        return self._output_path

    def to_asciidoctor_options(self):
        return ''

    def needed_host_paths(self):
        return []
