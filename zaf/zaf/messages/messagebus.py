import itertools
import logging
from collections import OrderedDict, defaultdict, namedtuple
from threading import RLock
from time import sleep, time

from zaf.utils.future import Future, FuturesCollection

from .message import Message

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

DispatcherState = namedtuple('DispatcherState', ['dispatcher', 'active_count', 'queue_count'])
EndpointState = namedtuple('EndpointState', ['endpoint', 'dispatcher_states'])


class NoSuchEndpoint(Exception):
    pass


class NoSuchMessage(Exception):
    pass


class NoSuchDispatcher(Exception):
    pass


class EndpointAlreadyDefined(Exception):
    pass


class MessageBusTimeout(Exception):
    pass


class MessageBus(object):
    """
    The MessageBus has knowledge about all defined EndPointIds and MessageIds.

    It handles the registration/deregistration of dispatchers and when messages are triggered
    the MessageBus triggers each applicable dispatcher with an Message object with all information
    about the message.
    """

    def __init__(self, component_factory, scope=None):
        self._endpoints = set()
        self._messages = OrderedDict()
        self.component_factory = component_factory
        self.scope = scope

    def is_endpoint_defined(self, endpoint):
        """
        Check if an endpoint is defined.

        :param endpoint: the EndpointId of the endpoint
        :return: True/False if endpoint is defined or not
        """
        return endpoint in self._endpoints

    def is_message_defined_for_endpoint(self, message_id, endpoint):
        """
        Check if an MessageId is defined for a EndpointId.

        :param message_id: the message
        :param endpoint: the endpoint
        :return: True/False if message is defined for the endpoint
        """
        return message_id in self._messages and self._messages[message_id].is_endpoint_defined(
            endpoint)

    def get_defined_messages_and_endpoints(self):
        """
        Retrieve a dictionary mapping messages to a list of endpoints for each message.

        :return: dict from MessageId to list of EndpointIds
        """

        return {
            message.message_id: [endpoint.endpoint_id for endpoint in message.endpoints]
            for message in self._messages.values()
        }

    def get_defined_endpoints_and_messages(self):
        """
        Retrieve a dictionary mapping endpoints to a list of messages for each endpoint.

        :return: dict from EndpointId to list of MessageIds
        """
        endpoints_and_messages = OrderedDict()
        for endpoint_id in self._endpoints:
            message_ids = []
            endpoints_and_messages[endpoint_id] = message_ids

            for message_id, message_registry in self._messages.items():
                if self.is_message_defined_for_endpoint(message_id, endpoint_id):
                    message_ids.append(message_id)

        return endpoints_and_messages

    def define_endpoints_and_messages(self, endpoints_and_messages):
        """
        Define multiple endpoints and messages.

        :param endpoints_and_messages: dict from EndpointId to list of MessageIds
        """
        for endpoint_id, message_id in endpoints_and_messages.items():
            self.define_endpoint(endpoint_id)
            for message_id in message_id:
                self.define_message(message_id, endpoint_id)

    def define_endpoint(self, endpoint_id):
        """
        Define a new EndpointId in the MessageBus.

        :param endpoint_id: the EndpointId to define
        :raises: EndpointAlreadyDefined if endpoint is already defined
        """
        logger.debug("Defining endpoint '%s'", endpoint_id.name)
        if self.is_endpoint_defined(endpoint_id):
            raise EndpointAlreadyDefined(
                "Endpoint '{endpoint}' already defined".format(endpoint=endpoint_id.name))
        self._endpoints.add(endpoint_id)

    def define_message(self, message_id, endpoint_id):
        """
        Define a new MessageId for a EndpointId.

        :param message_id: the message
        :param endpoint_id: the endpoint
        :raises: NoSuchEndpoint if the endpoint isn't defined
        :raises: EndpointAlreadyDefined if the endpoint is already defined for specified message
        """
        logger.debug("Defining message '%s' for endpoint '%s'", message_id.name, endpoint_id.name)
        if endpoint_id in self._endpoints:
            if message_id not in self._messages:
                self._messages[message_id] = MessageDispatcherRegistry(message_id)
            self._messages[message_id].define_endpoint(endpoint_id)
        else:
            raise NoSuchEndpoint(
                "Trying to define message '{message}' for unknown endpoint '{endpoint}'".format(
                    message=message_id.name, endpoint=endpoint_id.name))

    def register_dispatcher(self, dispatcher, message_ids, endpoint_ids=None, entities=None):
        """
        Register an message dispatcher to the MessageBus.

        :param message_ids: the MessageIds to register the dispatcher to
        :param dispatcher: the dispatcher
        :param endpoint_ids: the EndpointIds to register the dispatcher to
        :param entities: the entities to register the dispatcher for
        """
        endpoint_ids = endpoint_ids if endpoint_ids else []

        if not message_ids:
            raise ValueError('No message_ids specified when registering dispatcher')

        for message_id in message_ids:

            log_endpoint_part = 'all endpoints' if not endpoint_ids else "endpoints '{endpoints}'".format(
                endpoints=','.join([id.name for id in endpoint_ids]))
            log_entity_part = '' if not entities else " and entities '{entities}'".format(
                entities=','.join(entities))
            logger.debug(
                "Registering dispatcher for message '{message}' for {endpoint_part}{entities_part}".
                format(
                    message=message_id.name,
                    endpoint_part=log_endpoint_part,
                    entities_part=log_entity_part))

            if message_id in self._messages:
                self._messages[message_id].register(dispatcher, endpoint_ids, entities)
            else:
                raise NoSuchMessage(
                    "Trying to register dispatcher for unknown message '{message}'".format(
                        message=message_id.name))

    def deregister_dispatcher(self, dispatcher, message_ids=None, endpoint_ids=None, entities=None):
        """
        Deregisteres a dispatcher from the messages_ids for endpoint_ids and entities.

        If None is given for message_ids, endpoint_ids or entities that means match against all registered.
        If None is given for all then the dispatcher will be completely deregistered from the messagebus.

        :param dispatcher: The dispatcher to deregister
        :param message_ids: the message_ids for which to deregister the dispatcher
        :param endpoint_ids: the endpoint_ids for which to deregister the dispatcher
        :param entities: the entities for which to deregister the dispatcher
        :return: True if dispatcher still has registrations, False otherwise
        """
        endpoint_ids = endpoint_ids if endpoint_ids else []

        if message_ids is None:
            logger.debug(
                "Deregistering dispatcher '{dispatcher}' for all messages".format(
                    dispatcher=dispatcher.log_repr()))
            deregistered = False
            for registry in self._messages.values():
                try:
                    registry.deregister(dispatcher, endpoint_ids, entities)
                    deregistered = True
                except NoSuchDispatcher:
                    pass

            if not deregistered:
                endpoints_string = ','.join(
                    [id.name for id in endpoint_ids]) if endpoint_ids else 'all'
                raise NoSuchDispatcher(
                    "Trying to deregister unknown dispatcher from '{endpoints}'".format(
                        endpoints=endpoints_string))
        elif len(message_ids) == 0:
            raise ValueError('deregister_dispatcher is not valid for empty list of message_ids')
        else:
            for message_id in message_ids:
                logger.debug("Deregistering dispatcher for message '%s'", message_id.name)
                if message_id in self._messages:
                    self._messages[message_id].deregister(dispatcher, endpoint_ids, entities)
                else:
                    raise NoSuchMessage(
                        "Trying to deregister dispatcher for unknown message '{message}'".format(
                            message=message_id.name))

            return self.dispatcher_is_registered(dispatcher)

    def trigger_event(self, message_id, sender_endpoint_id, entity=None, data=None):
        """
        Send a message that should trigger all applicable dispatcher.

        The order dispatchers are triggered in is controlled by the priority attribute.

        :param message_id: the MessageId of the message that should be sent
        :param sender_endpoint_id: The EndpointId of the endpoint that sent the message
        :param data: The message data
        """
        logger.debug(
            "Triggering event '{message}' from endpoint '{endpoint}'{entity_part}".format(
                message=message_id.name,
                endpoint=sender_endpoint_id.name,
                entity_part='' if not entity else " for entity '{entity}'".format(entity=entity)))
        if message_id in self._messages:
            message_registry = self._messages[message_id]
            dispatchers_and_messages = []
            for endpoint in message_registry.endpoints:
                if sender_endpoint_id == endpoint.endpoint_id:
                    for dispatcher_entity, dispatchers in message_registry.dispatchers_for_endpoint(
                            endpoint, None, entity).items():
                        message = Message(
                            message_id, sender_endpoint_id, entity
                            if entity else dispatcher_entity, data)
                        for dispatcher in dispatchers:
                            dispatchers_and_messages.append((dispatcher, message))
            for dispatcher, message in sorted(dispatchers_and_messages, key=lambda x: x[0].priority,
                                              reverse=True):
                dispatcher.dispatch(message)

        else:
            raise NoSuchMessage(
                "Trying to send unknown message '{message}' from endpoint '{endpoint}'".format(
                    message=message_id.name, endpoint=sender_endpoint_id.name))

    def send_request(self, message_id, receiver_endpoint_id=None, entity=None, data=None):
        """
        Send a request to all applicable targets.

        The order dispatchers are triggered in is controlled by the priority attribute.

        :param message_id: The MessageId of the request that should be sent
        :param receiver_endpoint_id: The EndpointId of the recipients of the messages
        :para data: The message data
        """
        futures = FuturesCollection()

        log_endpoint_part = 'all endpoints' if not receiver_endpoint_id else "endpoint '{endpoint}'".format(
            endpoint=receiver_endpoint_id.name)
        logger.debug(
            "Sending request '{message}' to {endpoint_part}{entity_part}".format(
                message=message_id.name,
                endpoint_part=log_endpoint_part,
                entity_part='' if not entity else " for entity '{entity}'".format(entity=entity)))
        if message_id in self._messages:
            message_registry = self._messages[message_id]
            dispatchers_and_messages = []
            for endpoint in self._messages[message_id].endpoints:
                if receiver_endpoint_id is None or receiver_endpoint_id == endpoint.endpoint_id:
                    for dispatcher_entity, dispatchers in message_registry.dispatchers_for_endpoint(
                            endpoint, entity, all_entities=entity is None).items():
                        for dispatcher in dispatchers:
                            future = Future()
                            message = Message(
                                message_id, receiver_endpoint_id, entity
                                if entity else dispatcher_entity, data, future)
                            dispatchers_and_messages.append((dispatcher, message))
                            futures.append(future)
            for dispatcher, message in sorted(dispatchers_and_messages, key=lambda x: x[0].priority,
                                              reverse=True):
                dispatcher.dispatch(message)

        return futures

    def has_registered_dispatchers(self, message, endpoint_id, entity=None):
        if message not in self._messages:
            return False
        else:
            message_registry = self._messages[message]
            endpoint = [
                endpoint for endpoint in message_registry.endpoints
                if endpoint_id == endpoint.endpoint_id
            ]

            if endpoint:
                return len(message_registry.dispatchers_for_endpoint(endpoint[0],
                                                                     entity).values()) > 0
            else:
                return False

    def dispatcher_is_registered(self, dispatcher):
        for message_id, message_registry in self._messages.items():
            for endpoint_registry in message_registry.endpoints:
                if endpoint_registry.has_dispatcher(dispatcher):
                    return True

        return False

    def wait_for_not_active(self, endpoint_id=None, timeout=3):
        """
        Wait for endpoint to finish current work and queue, or all endpoints if not specified.

        :param endpoint_id: The EndpointId of the endpoint to wait for
        :param timeout: How long to wait in seconds
        """
        start = time()
        while self.is_active(endpoint_id):
            if not (time() - start) < timeout:
                msg_lines = []

                for endpoint_state in self.get_state():
                    active_dispatchers = [
                        dispatcher_state for dispatcher_state in endpoint_state.dispatcher_states
                        if dispatcher_state.active_count > 0 or dispatcher_state.queue_count > 0
                    ]

                    if active_dispatchers:
                        msg_lines.append(
                            '  {endpoint_name}:'.format(endpoint_name=endpoint_state.endpoint.name))
                        for dispatcher_state in active_dispatchers:
                            msg_lines.append(
                                '    {name}: queue_count={queue}, active_count={active}'.format(
                                    name=dispatcher_state.dispatcher,
                                    queue=dispatcher_state.queue_count,
                                    active=dispatcher_state.active_count))

                raise MessageBusTimeout(
                    'Waiting for MessageBus activity to stop timed out:\n{msg}'.format(
                        msg='\n'.join(msg_lines)))
            sleep(0.001)

    def get_state(self, endpoint_id=None):
        """
        Get execution state of endpoint, or all endpoints if not specified.

        :param endpoint_id: The EndpointId of the endpoint to get state for
        :return: List of EndpointStates
        """
        if endpoint_id:
            return [self._get_endpoint_state(endpoint_id)]
        else:
            state = []
            for endpoint in self._endpoints:
                state.append(self._get_endpoint_state(endpoint))
            return state

    def is_active(self, endpoint_id=None):
        """
        Check if endpoint is active, or all endpoints if not specified.

        :param endpoint_id: The EndpointId of the endpoint to check if active
        :return: True if specified/any endpoint is active, else False
        """
        for state in self.get_state(endpoint_id):
            if self._is_active(state):
                return True
        return False

    def _is_active(self, endpoint_state):
        for dispatcher_state in endpoint_state.dispatcher_states:
            if dispatcher_state.active_count or dispatcher_state.queue_count:
                return True
        return False

    def _get_endpoint_state(self, endpoint_id):
        if not self.is_endpoint_defined(endpoint_id):
            raise NoSuchEndpoint(
                "Trying to get state for unknown endpoint '{endpoint}'".format(
                    endpoint=endpoint_id.name))
        state = EndpointState(endpoint_id, [])
        for dispatcher in self._get_dispatchers_for_endpoint(endpoint_id):
            active_count = dispatcher.get_active_count()
            queue_count = dispatcher.get_queue_count()
            state.dispatcher_states.append(
                DispatcherState(dispatcher.log_repr(), active_count, queue_count))
        return state

    def get_dispatchers(self):
        dispatchers = []
        for endpoint in self.get_defined_endpoints_and_messages().keys():
            for dispatcher in self._get_dispatchers_for_endpoint(endpoint):
                dispatchers.append(dispatcher.log_repr())
        return dispatchers

    def _get_dispatchers_for_endpoint(self, endpoint_id):
        dispatchers = []
        endpoints_and_messages = self.get_defined_endpoints_and_messages()
        for message in endpoints_and_messages[endpoint_id]:
            for endpoint in self._messages[message]._endpoints:
                if endpoint._endpoint_id == endpoint_id:
                    dispatchers += (list(endpoint._dispatchers.values()))
        return [item for sublist in dispatchers for item in sublist]


class MessageDispatcherRegistry(object):
    """
    Keeps information about all defined endpoints and registered dispatchers for a specific message.

    This class is sychronized to guard against registration/deregistration being performed
    in different threads at the same time as messages are being triggered
    """

    def __init__(self, endpoint_id):
        """
        Create a new MessageDispatcherRegistry for the specified MessageId.

        :param endpoint_id: the MessageID
        """
        self._message_id = endpoint_id
        self._endpoints = []
        self._dispatchers = []
        self._lock = RLock()

    def define_endpoint(self, endpoint_id):
        """
        Define a new endpoint in this message.

        :param endpoint_id: the EndpointId
        :raises: EndpointAlreadyDefined if the endpoint is already defined in this registry
        """
        if self.is_endpoint_defined(endpoint_id):
            raise EndpointAlreadyDefined(
                'Endpoint {endpoint} already defined for message {message}'.format(
                    endpoint=endpoint_id.name, message=self.message_id.name))
        self._endpoints.append(Endpoint(endpoint_id))

    def is_endpoint_defined(self, endpoint_id):
        """
        Check if a endpoint is already defined for this message.

        :param endpoint_id: the EndpointId
        :return: True/False if endpoint is defined or not
        """
        return len(
            [endpoint for endpoint in self._endpoints if endpoint.endpoint_id == endpoint_id])

    def register(self, dispatcher, endpoint_ids, entities=None):
        """
        Register a dispatcher to the registry.

        :param dispatcher: the dispatcher
        :param endpoint_ids: the EndpointIds to register for
        :param entities: the entities to register for
        :raises: NoSuchEndpoint if trying to register to a endpoint that isn't registered
        """
        for endpoint_id in endpoint_ids:
            matching_endpoints = \
                [endpoint.endpoint_id for endpoint in self._endpoints if endpoint.endpoint_id == endpoint_id]
            if len(matching_endpoints) == 0:
                raise NoSuchEndpoint(
                    'Trying to register dispatcher for message {message} to unknown endpoint {endpoint}'.
                    format(message=self._message_id.name, endpoint=endpoint_id.name))
        with self._lock:
            if endpoint_ids:
                for endpoint in self._endpoints:
                    if endpoint.endpoint_id in endpoint_ids:
                        endpoint.add_dispatcher(dispatcher, entities)
            else:
                for endpoint in self._endpoints:
                    endpoint.add_dispatcher(dispatcher, entities)

    def deregister(self, dispatcher, endpoint_ids, entities=None):
        """
        Deregister a dispatcher from the registry.

        :param dispatcher: the dispatcher callable
        :param endpoint_ids: the EndpointIds to deregister for
        :param entities: specific entities to deregister for, all if None are provided
        :raises: NoSuchDispatcher if trying to derigister from a dispatcher that doesn't exit
        """
        remove_count = 0
        with self._lock:
            all_entities = entities is None
            if endpoint_ids:
                for endpoint, endpoint_id in itertools.product(self._endpoints, endpoint_ids):
                    if dispatcher in itertools.chain(*endpoint.get_dispatchers(
                            entities, all_entities=all_entities).values()):
                        endpoint.remove_dispatcher(dispatcher, entities)
                        remove_count += 1
            else:
                for endpoint in self._endpoints:
                    if dispatcher in itertools.chain(*endpoint.get_dispatchers(
                            entities, all_entities=all_entities).values()):
                        endpoint.remove_dispatcher(dispatcher, entities)
                        remove_count += 1

        if remove_count == 0:
            raise NoSuchDispatcher(
                "Trying to deregister unknown dispatcher for message '{message}' from '{endpoints}'".
                format(
                    message=self._message_id.name,
                    endpoints=','.join([id.name for id in endpoint_ids])
                    if endpoint_ids else 'all'))

    @property
    def endpoints(self):
        return self._endpoints

    def dispatchers_for_endpoint(self, endpoint, *entities, all_entities=False):
        with self._lock:
            return endpoint.get_dispatchers(entities, all_entities=all_entities)

    @property
    def message_id(self):
        return self._message_id


class Endpoint(object):

    def __init__(self, endpoint_id):
        self._endpoint_id = endpoint_id
        self._dispatchers = {}

    def add_dispatcher(self, dispatcher, entities=None):
        for entity in entities if entities else [None]:
            if entity not in self._dispatchers:
                self._dispatchers[entity] = []

            self._dispatchers[entity].append(dispatcher)

    def remove_dispatcher(self, dispatcher, entities=None):
        for key, dispatchers in self._dispatchers.items():
            if entities is None and dispatcher in self._dispatchers[key]:
                self._dispatchers[key].remove(dispatcher)
            elif entities is not None and key in entities:
                self._dispatchers[key].remove(dispatcher)

    def get_dispatchers(self, entities, all_entities=False):
        dispatchers = defaultdict(list)
        for entity, entity_dispatchers in self._dispatchers.items():
            if all_entities is True or entity in entities:
                for dispatcher in entity_dispatchers:
                    if dispatcher not in dispatchers:
                        dispatchers[entity].append(dispatcher)
        return dispatchers

    def has_dispatcher(self, dispatcher):
        for entity, dispatchers in self._dispatchers.items():
            if dispatcher in dispatchers:
                return True
        return False

    @property
    def endpoint_id(self):
        return self._endpoint_id
