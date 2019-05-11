from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId

LEVELS_IDS = ConfigOptionId(
    'ids', 'Defines the different document levels.', multiple=True, entity=True, namespace='levels')

LEVEL_INCLUDES = ConfigOptionId(
    'includes',
    'Defines what should be included in sections with this level.',
    multiple=True,
    at=LEVELS_IDS)

LEVEL_EXCLUDES = ConfigOptionId(
    'excludes',
    'Defines what should be excluded in sections with this level.',
    multiple=True,
    at=LEVELS_IDS)

MAGIC_TITLES = ConfigOptionId(
    'magic.titles',
    'Magic titles that should be handled as known structure elements.',
    multiple=True,
)

KEEP_EMPTY_SECTIONS = ConfigOptionId(
    'keep.empty.sections',
    'If true empty sections will be kept in the generated document.',
    option_type=bool,
    default=False)

MAX_ALLOWED_VERSION = ConfigOptionId(
    'max.allowed.version',
    'If provided this is the highest version that will be kept in the generated document.',
    option_type=str)

KEEP_ALL_VERSIONS = ConfigOptionId(
    'keep.all.versions', (
        'If set all verions of a section with a given ID will be included in the generated document. '
        'Otherwise, only the latest version is kept.'),
    option_type=bool,
    default=False)

ASCIIDOCTOR_DOCSTRUCTURE_ENDPOINT = EndpointId(
    'ASCIIDOCTOR_DOCSTRUCTURE_ENDPOINT', 'Endpoint that handles the document structure')
