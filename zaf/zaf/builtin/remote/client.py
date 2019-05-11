import logging
import pickle
import time

import rpyc

from zaf.builtin.remote import REMOTE_CLIENT_ENABLED, REMOTE_CLIENT_HOST, REMOTE_CLIENT_PORT
from zaf.component.decorator import component
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, FrameworkExtension

logger = logging.getLogger(__name__)


class RemoteError(Exception):
    pass


@FrameworkExtension(
    name='remote',
    config_options=[
        ConfigOption(REMOTE_CLIENT_ENABLED, required=True),
        ConfigOption(REMOTE_CLIENT_PORT, required=True),
        ConfigOption(REMOTE_CLIENT_HOST, required=True),
    ])
class RemoteClientExtension(AbstractExtension):
    """Client for remote connection implementing the remote interface."""

    def __init__(self, config, instances):
        if config.get(REMOTE_CLIENT_ENABLED):

            @component(name='RemoteClient')
            def remote_client():
                return RemoteClient(
                    host=config.get(REMOTE_CLIENT_HOST), port=config.get(REMOTE_CLIENT_PORT))


class RemoteClient(object):
    """Remote client that can communicate with a remote server."""

    def __init__(self, host='localhost', port=18861):
        self.connection = None
        self.host = host
        self.port = port

    def connect(self, tries=100, timeout_between_tries=0.1):
        self.connection = None
        connected = False
        while not connected and tries > 0:
            try:
                self.connection = rpyc.connect(
                    self.host, self.port, config={
                        'allow_all_attrs': True
                    })
                connected = True
            except Exception:
                time.sleep(timeout_between_tries)
                tries -= 1
        if not connected:
            msg = 'Failed to connect to {host}:{port}'.format(host=self.host, port=self.port)
            logger.error(msg)
            raise RemoteError(msg)

    def close(self):
        if self.connection:
            self.connection.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def trigger_event(self, message_id, endpoint_id, entity=None, data=None):
        """
        Trigger an event using the remote connection.

        :param message_id: The message_id of the event
        :param endpoint_id: The endpoint_id of the sender of the event
        :param entity: The entity of the sender of the event
        :param data: The event data
        """
        logger.debug(
            'Triggering remote event {message_id} with endpoint {endpoint} and entity {entity}'.
            format(message_id=message_id.name, endpoint=endpoint_id.name, entity=entity))
        self.connection.root.trigger_event(
            pickle.dumps(message_id), pickle.dumps(endpoint_id), pickle.dumps(entity),
            pickle.dumps(data))

    def send_request(self, message_id, endpoint_id=None, entity=None, data=None, is_async=False):
        """
        Send a request using the remote connection.

        :param message_id: The message_id of the request
        :param endpoint_id: The endpoint_id of the receiver of the request
        :param entity: The entity of the receiver of the request
        :param data: The request data
        :param async: Tells the server to not respond with the futures collection
                      This is useful to not get problems when server closes immediately after receiving
                      the request because then the remote connection is destroyed before the futures
                      collection can be handled by the client.
        """
        logger.debug(
            'Sending remote request {message_id} with endpoint {endpoint} and entity {entity}'.
            format(
                message_id=message_id.name,
                endpoint=endpoint_id.name if endpoint_id else None,
                entity=entity))
        return self.connection.root.send_request(
            pickle.dumps(message_id), pickle.dumps(endpoint_id), pickle.dumps(entity),
            pickle.dumps(data), is_async)

    def local_message_queue(self, message_ids, endpoint_ids=None, entities=None):
        """
        Register a LocalMessageQueue to the messagebus using the remote connection.

        :param message_ids: The message_ids to listen to
        :param endpoint_ids: The endpoint_ids to listen to
        :param entities: The entities to listen to
        """
        logger.debug(
            'Creating remote message queue for {message_ids}'.format(
                message_ids=', '.join([id.name for id in message_ids])))
        return self.connection.root.local_message_queue(
            pickle.dumps(message_ids), pickle.dumps(endpoint_ids), pickle.dumps(entities))

    def define_endpoints_and_messages(self, endpoints_and_messages):
        """
        Define new endpoints and messages in the messagebus using the remote connection.

        :param endpoints_and_messages: The endpoints and messages to register.
                                       Dict from EndpointId to list of MessageId.
        """
        logger.debug(
            'Defining endpoints and messages {endpoints_and_messages}'.format(
                endpoints_and_messages=endpoints_and_messages))
        return self.connection.root.define_endpoints_and_messages(
            pickle.dumps(endpoints_and_messages))
