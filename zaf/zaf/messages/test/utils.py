from unittest.mock import Mock

from zaf.component.factory import Factory
from zaf.component.manager import ComponentManager

from ..message import EndpointId, MessageId
from ..messagebus import MessageBus

data = {'k1': 'v1', 'zaf': 'v2'}

defined_endpoint = EndpointId('defined_endpoint', '')
defined_endpoint2 = EndpointId('defined_endpoint2', '')
notdefined_endpoint = EndpointId('notdefined_endpoint', '')

defined_message = MessageId('defined_message', '')
defined_message2 = MessageId('defined_message2', '')
defined_message3 = MessageId('defined_message3', '')
notdefined_message = MessageId('notdefined_message', '')

entity = 'entity'
entity2 = 'entity2'


def create_dispatcher(trigger_function=None, priority=0, log_repr=None):
    mock = Mock()
    mock.priority = priority
    mock.log_repr.return_value = log_repr
    if trigger_function:
        mock.dispatch.side_effect = trigger_function
    return mock


def create_messagebus():
    factory = Factory(ComponentManager())
    messagebus = MessageBus(factory, factory.enter_scope('session', None))
    messagebus.define_endpoint(defined_endpoint)
    messagebus.define_endpoint(defined_endpoint2)
    messagebus.define_message(defined_message, defined_endpoint)
    messagebus.define_message(defined_message, defined_endpoint2)
    messagebus.define_message(defined_message2, defined_endpoint2)
    messagebus.define_message(defined_message3, defined_endpoint2)
    return messagebus
