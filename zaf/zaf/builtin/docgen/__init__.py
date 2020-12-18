from collections import namedtuple

from zaf.messages.message import MessageId, EndpointId

DocTemplate = namedtuple('DocTemplate', ['package', 'template_dir', 'filename'])

DOCGEN_COMMAND_ENDPOINT = EndpointId(
    'DOCGEN_COMMAND_ENDPOINT', """Endpoint for the docgen command.""")

GET_CUSTOM_LOGGING_DOCS = MessageId(
    'GET_CUSTOM_LOGGING_DOCS', """
    Get path to template file with custom logging documentation
    that should be injected into the generated documentation.

    return: list of DocTemplate
    """)

GET_CUSTOM_DOCS = MessageId(
    'GET_CUSTOM_DOCS', """
    Get list of paths to templates that should be rendered
    and included in the generated documentation.

    return: list of DocTemplate
    """)

GET_CUSTOM_DOC_FILES = MessageId(
    'GET_CUSTOM_DOC_FILES', """
    Get list of files that need to be put in the same directory as the documentation.

    return: list of DocTemplate
    """)
