from zaf.builtin.blocker import BLOCKER_ENDPOINT, BLOCKING_COMPLETED, BLOCKING_STARTED, \
    START_BLOCKING_ON_MESSAGE, STOP_BLOCKING_ON_MESSAGE, StartBlockingInfo
from zaf.commands.command import CommandId
from zaf.component.decorator import requires
from zaf.extensions.extension import AbstractExtension, FrameworkExtension
from zaf.messages.decorator import concurrent_dispatcher
from zaf.messages.dispatchers import LocalMessageQueue
from zaf.messages.message import EndpointId, MessageId

BLOCK_MESSAGE = MessageId('BLOCK_MESSAGE', '')
START = MessageId('START', '')
CONTINUE = MessageId('CONTINUE', '')
ENDPOINT = EndpointId('ENDPOINT', '')


def remote_and_blocker_command(core):
    core.messagebus.send_request(START, receiver_endpoint_id=ENDPOINT)
    core.component_factory.call(_remote_and_blocker_command, core.session_scope)


@requires(client='RemoteClient')
def _remote_and_blocker_command(client):
    # Request that waits for CONTINUE to have been received by the test case
    # which indicates that test case message and endpoint have been defined
    client.send_request(CONTINUE, ENDPOINT).wait(timeout=1)[0].result(timeout=1)

    # Register the blocking and receive the blocking ID so that it can be used in the
    # local message queue registration
    blocking_id = client.send_request(
        START_BLOCKING_ON_MESSAGE,
        data=StartBlockingInfo(
            message_id=BLOCK_MESSAGE, endpoint_id=ENDPOINT, entity=None,
            timeout=5)).wait(timeout=1)[0].result(timeout=1)

    with client.local_message_queue(message_ids=[BLOCKING_STARTED, BLOCKING_COMPLETED],
                                    endpoint_ids=[BLOCKER_ENDPOINT],
                                    entities=[blocking_id]) as queue:
        # Send continue again so that test case triggers BLOCK_MESSAGE
        client.send_request(CONTINUE, ENDPOINT).wait(timeout=1)[0].result(timeout=1)

        # Wait for testcase to send the message that we want to block on
        assert queue.get(timeout=1).message_id.name == BLOCKING_STARTED.name

        # Send CONTINUE before stopping blocking so that it exists in the testcase queue
        # on next get. This verifies that the block actually blocked the test case
        client.send_request(CONTINUE, ENDPOINT).wait(timeout=1)

        # Stop blocking and verify that the blocking completed without problems
        client.send_request(STOP_BLOCKING_ON_MESSAGE, entity=blocking_id)
        assert queue.get(timeout=1).message_id.name == BLOCKING_COMPLETED.name

        # Send a final continue to test case. This is needed because otherwise the remote server
        # will be stopped before the BLOCKING_COMPLETED message has been received
        client.send_request(CONTINUE, ENDPOINT, is_async=True)

        print('Reached end of command')


def remote_and_blocker_using_blocker_component_command(core):
    core.messagebus.send_request(START, receiver_endpoint_id=ENDPOINT)
    core.component_factory.call(
        _remote_and_blocker_using_blocker_component_command, core.session_scope)


@requires(client='RemoteClient')
def _remote_and_blocker_using_blocker_component_command(client, RemoteBlocker):
    # Request that waits for CONTINUE to have been received by the test case
    # which indicates that test case message and endpoint have been defined
    client.send_request(CONTINUE, ENDPOINT).wait(timeout=1)[0].result(timeout=1)

    with RemoteBlocker(BLOCK_MESSAGE, ENDPOINT, None, timeout=5, remote=client) as blocker:
        # Send continue again so that test case triggers BLOCK_MESSAGE
        client.send_request(CONTINUE, ENDPOINT).wait(timeout=1)[0].result(timeout=1)

        blocker.wait_for_started(timeout=1)

        # Send CONTINUE before stopping blocking so that it exists in the testcase queue
        # on next get. This verifies that the block actually blocked the test case
        client.send_request(CONTINUE, ENDPOINT).wait(timeout=1)

        blocker.stop_blocking()
        assert blocker.wait_for_finished()

        # Send a final continue to test case. This is needed because otherwise the remote server
        # will be stopped before the BLOCKING_COMPLETED message has been received
        client.send_request(CONTINUE, ENDPOINT, is_async=True)

    print('Reached end of command')


REMOTE_AND_BLOCKER_COMMAND = CommandId(
    'remoteandblockercommand', '', remote_and_blocker_command, config_options=[])

REMOTE_AND_BLOCKER_USING_BLOCKER_COMPONENT_COMMAND = CommandId(
    'remoteandblockerusingblockercomponentcommand',
    '',
    remote_and_blocker_using_blocker_component_command,
    config_options=[])


@FrameworkExtension(
    'usestheblockerandremotefacilitiesextension',
    commands=[REMOTE_AND_BLOCKER_COMMAND, REMOTE_AND_BLOCKER_USING_BLOCKER_COMPONENT_COMMAND],
    endpoints_and_messages={
        ENDPOINT: [BLOCK_MESSAGE, CONTINUE, START],
    },
)
class UsesTheBlockerAndRemoteFacilitiesExtension(AbstractExtension):

    @concurrent_dispatcher(message_ids=[START], endpoint_ids=[ENDPOINT])
    @requires(messagebus='MessageBus')
    def _handle_start(self, message, messagebus):
        with LocalMessageQueue(messagebus, [CONTINUE], [ENDPOINT]) as cont:
            assert cont.get(timeout=1).message_id == CONTINUE
            assert cont.get(timeout=1).message_id == CONTINUE

            messagebus.trigger_event(BLOCK_MESSAGE, ENDPOINT)
            assert cont.get(timeout=0)
            assert cont.get(timeout=1)
