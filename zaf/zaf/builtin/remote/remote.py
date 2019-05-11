"""
Provides a RPC client and server for communicating with an ongoing Zaf process.

A remote procedure call implementation using `rpyc <https://rpyc.readthedocs.io/en/latest/>`_.
When configured this starts a server inside Zaf that listens to the specified port.

The remote client can be used to communicate with another Zaf process.
This is used especially in the systest to synchronize the test case with the started Zaf process.

The provided remote calls are

trigger_event(message_id, endpoint_id, entity=None, data=None):
    Triggers an event using the remote connection

    :message_id: The message_id of the event
    :endpoint_id: The endpoint_id of the sender of the event
    :entity: The entity of the sender of the event
    :data: The event data

send_request(message_id, endpoint_id=None, entity=None, data=None, async=False):
    Sends a request using the remote connection

    :message_id: The message_id of the request
    :endpoint_id: The endpoint_id of the receiver of the request
    :entity: The entity of the receiver of the request
    :data: The request data
    :async: Tells the server to not respond with the futures collection
                  This is useful to not get problems when server closes immediately after receiving
                  the request because then the remote connection is destroyed before the futures
                  collection can be handled by the client.

local_message_queue(message_ids, endpoint_ids=None, entities=None):
    Registers a LocalMessageQueue to the messagebus using the remote connection.

    :message_ids: The message_ids to listen to
    :endpoint_ids: The endpoint_ids to listen to
    :entities: The entities to listen to

define_endpoints_and_messages(endpoints_and_messages):
    Defines new endpoints and messages in the messagebus using the remote connection.

    :endpoints_and_messages: The endpoints and messages to register.
                                   Dict from EndpointId to list of MessageId.
"""
import logging
import pickle
import time
from threading import Thread

import rpyc
from rpyc.utils.server import ThreadedServer

from zaf.application import AFTER_COMMAND, APPLICATION_ENDPOINT
from zaf.builtin.remote import REMOTE_ENABLED, REMOTE_PORT
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, FrameworkExtension
from zaf.messages.decorator import callback_dispatcher
from zaf.messages.dispatchers import LocalMessageQueue

logger = logging.getLogger(__name__)


@FrameworkExtension(
    'remote',
    config_options=[
        ConfigOption(REMOTE_ENABLED, required=True),
        ConfigOption(REMOTE_PORT, required=True),
    ],
    activate_on=[REMOTE_ENABLED],
)
class RemoteServer(AbstractExtension):
    """Server for remote connections that provides messagebus functionality to users outside of Zaf."""

    def __init__(self, config, instances):
        self._enabled = config.get(REMOTE_ENABLED)
        self._port = config.get(REMOTE_PORT)
        self.server = None
        self.thread = None

    def is_running(self):
        return self.server and self.thread and self.thread.is_alive()

    def register_dispatchers(self, messagebus):
        if self._enabled:
            self.server = ThreadedServer(
                create_service(messagebus),
                port=self._port,
                reuse_addr=True,
                protocol_config={'allow_all_attrs': True},
                logger=logger)

            self.thread = Thread(target=self.server.start)
            self.thread.start()

    @callback_dispatcher([AFTER_COMMAND], [APPLICATION_ENDPOINT])
    def close_server(self, message=None):
        self.destroy()

    def destroy(self):
        try:
            if self.is_running():
                logger.debug('Stopping remote server')
                if len(self.server.clients) > 0:
                    # If all clients haven't been closed yet we will wait for a short time
                    # This can happen in systests because the close of zzaf is too quick for
                    # a clean disconnect
                    logger.debug(
                        'Clients still connected. Waiting 0.1 seconds before hard close of remote server'
                    )
                    time.sleep(0.1)
                self.server.close()
                self.thread.join()
        finally:
            self._after_command_dispatcher = None


def create_service(messagebus_arg):

    class MessageBusService(rpyc.Service):
        messagebus = messagebus_arg

        def on_connect(self):
            pass

        def on_disconnect(self):
            pass

        def exposed_trigger_event(
                self, serialized_message_id, serialized_endpoint_id, serialized_entity,
                serialized_data):
            message_id = pickle.loads(serialized_message_id)
            endpoint_id = pickle.loads(serialized_endpoint_id)
            entity = pickle.loads(serialized_entity)
            data = pickle.loads(serialized_data)

            logger.debug(
                'Triggering remote event {message} with endpoint {endpoint} and entity {entity}'.
                format(message=message_id.name, endpoint=endpoint_id.name, entity=entity))

            self.messagebus.trigger_event(message_id, endpoint_id, entity, data)

        def exposed_send_request(
                self,
                serialized_message_id,
                serialized_endpoint_id,
                serialized_entity,
                serialized_data,
                is_async=False):
            message_id = pickle.loads(serialized_message_id)
            endpoint_id = pickle.loads(serialized_endpoint_id)
            entity = pickle.loads(serialized_entity)
            data = pickle.loads(serialized_data)

            logger.debug(
                'Sending remote request {message} with endpoint {endpoint} and entity {entity}'.
                format(
                    message=message_id.name,
                    endpoint=None if not endpoint_id else endpoint_id.name,
                    entity=entity))

            futures = self.messagebus.send_request(message_id, endpoint_id, entity, data)
            if not is_async:
                return futures

        def exposed_local_message_queue(
                self, serialized_message_ids, serialized_endpoint_ids, serialized_entities):
            message_ids = pickle.loads(serialized_message_ids)
            endpoint_ids = pickle.loads(serialized_endpoint_ids)
            entities = pickle.loads(serialized_entities)

            return LocalMessageQueue(self.messagebus, message_ids, endpoint_ids, entities)

        def exposed_define_endpoints_and_messages(self, serialized_endpoints_and_messages):
            endpoints_and_messages = pickle.loads(serialized_endpoints_and_messages)

            self.messagebus.define_endpoints_and_messages(endpoints_and_messages)

    return MessageBusService
