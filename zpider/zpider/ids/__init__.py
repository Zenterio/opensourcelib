from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId

EXCLUDE_IDS = ConfigOptionId('exclude.ids', '', multiple=True)
INCLUDE_IDS = ConfigOptionId('include.ids', '', multiple=True)

ASCIIDOCTOR_IDS_ENDPOINT = EndpointId('ASCIIDOCTOR_IDS_ENDPOINT', 'Endpoint that handles ids')
