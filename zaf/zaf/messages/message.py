from collections import namedtuple
from textwrap import dedent

InternalEndPointId = namedtuple('InternalEndPointId', ['name', 'description'])
InternalMessageId = namedtuple('InternalMessageId', ['name', 'description'])


class EndpointId(InternalEndPointId):
    __slots__ = ()

    def __new__(cls, name, description):
        """
        Define a new EndpointId.

        :param name: the name of the endpoint
        :param description: description of the endpoint
        :return: new EndpointId
        """
        return super().__new__(cls, name, dedent(description).strip())


class MessageId(InternalMessageId):
    __slots__ = ()

    def __new__(cls, name, description):
        """
        Define a new MessageId.

        :param name: the name of the message
        :param description: description of the message
        :return: new MessageId
        """
        return super().__new__(cls, name, dedent(description).strip())


class Message(object):
    """Message object that is sent to dispatchers when a message is triggered."""

    def __init__(self, message_id, endpoint, entity=None, data=None, future=None):
        """
        Create a Message object.

        :param message_id: the MessageId object defining the message
        :param endpoint: the EndpointId object defining the endpoint
        :param entity: the entity that the message is sent for
        :param data: the data that should be included in the Message
        :param future: the future to execute this message in, may be None
        """
        self._message_id = message_id
        self._endpoint = endpoint
        self._entity = entity
        self._data = data
        self._future = future

    @property
    def message_id(self):
        return self._message_id

    @property
    def entity(self):
        return self._entity

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def data(self):
        return self._data

    @property
    def future(self):
        return self._future

    def __repr__(self):
        return 'Message: {{message_id: {name}, endpoint: {endpoint}, entity: {entity}, data: {data}}}'.format(
            name=self.message_id.name, endpoint=self.endpoint, entity=self.entity, data=self.data)

    def __str__(self):
        return self.message_id.name

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and self.message_id == other.message_id
            and self.endpoint == other.endpoint and self.data == other.data
            and self.entity == other.entity)
