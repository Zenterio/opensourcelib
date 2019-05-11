from zaf.config.options import ConfigOptionId
from zaf.messages.message import EndpointId, MessageId

INSTANCES = ConfigOptionId(
    'ids', 'description instance', multiple=True, namespace='instances', entity=True)

MY_EXTENSION_ENDPOINT = EndpointId(
    'MY_EXTENSION_ENDPOINT', """\
    This is my extensions endpoint
    """)

MY_EXTENSION_MESSAGE = MessageId(
    'MY_EXTENSION_MESSAGE', """
    This is my extensions message

    data: None
    """)
