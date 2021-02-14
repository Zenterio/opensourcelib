from zaf.builtin.blocker import BLOCKER_ENDPOINT, BLOCKING_COMPLETED, BLOCKING_STARTED, \
    BLOCKING_TIMED_OUT, START_BLOCKING_ON_MESSAGE, STOP_BLOCKING_ON_MESSAGE, StartBlockingInfo
from zaf.component.decorator import component, requires
from zaf.extensions.extension import AbstractExtension, FrameworkExtension


@component
class BlockerHelper(object):

    def stop_init_blocking(self, remote_client):
        remote_client.send_request(STOP_BLOCKING_ON_MESSAGE, entity='init')

    def stop_exit_blocking(self, remote_client):
        remote_client.send_request(STOP_BLOCKING_ON_MESSAGE, entity='exit', is_async=True)

    def stop_blocking(self, remote_client, id):
        remote_client.send_request(STOP_BLOCKING_ON_MESSAGE, entity=id)


@requires(remote='RemoteClient')
@component
class RemoteBlocker(object):

    def __init__(self, message_id, endpoint_id, entity, timeout, remote):
        self._remote = remote
        self._message_id = message_id
        self._endpoint_id = endpoint_id
        self._entity = entity
        self._timeout = timeout
        self._blocking_started_queue = None
        self._blocking_finished_queue = None
        self._blocking_id = None
        self._stop_blocking_sent = False

    def __enter__(self):
        # Register the blocking and receive the blocking ID so that it can be used in the
        # local message queue registration
        self._blocking_id = self._remote.send_request(
            START_BLOCKING_ON_MESSAGE,
            data=StartBlockingInfo(
                message_id=self._message_id,
                endpoint_id=self._endpoint_id,
                entity=self._entity,
                timeout=self._timeout)).wait(timeout=1)[0].result(timeout=1)

        self._blocking_started_queue = self._remote.local_message_queue(
            [BLOCKING_STARTED], [BLOCKER_ENDPOINT], entities=[self._blocking_id]).__enter__()

        self._blocking_finished_queue = self._remote.local_message_queue(
            [BLOCKING_COMPLETED, BLOCKING_TIMED_OUT], [BLOCKER_ENDPOINT],
            entities=[self._blocking_id]).__enter__()

        return self

    def stop_blocking(self):
        self._stop_blocking_sent = True
        self._remote.send_request(STOP_BLOCKING_ON_MESSAGE, entity=self._blocking_id)

    def wait_for_started(self, timeout=None):
        self._blocking_started_queue.get(timeout=timeout)

    def wait_for_finished(self, timeout=None):
        message = self._blocking_finished_queue.get(timeout=timeout)
        return message.message_id.name == BLOCKING_COMPLETED.name

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._blocking_started_queue:
                self._blocking_started_queue.__exit__(None, None, None)

            if self._blocking_finished_queue:
                self._blocking_finished_queue.__exit__(None, None, None)

            if not self._stop_blocking_sent:
                self.stop_blocking()
        except EOFError:
            # remote already disconnected
            pass


@FrameworkExtension(
    'remoteblockerextension', )
class RemoteBlockerExtension(AbstractExtension):
    pass
