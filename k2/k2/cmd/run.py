"""Provides the run command that is used to run K2 tests."""

import logging
from collections import namedtuple

from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import FrameworkExtension, get_logger_name
from zaf.messages.message import EndpointId, MessageId

from k2.sut import SUT

logger = logging.getLogger(get_logger_name('k2', 'runcommand'))
logger.addHandler(logging.NullHandler())

EXIT_CODE_FROM_VERDICT = ConfigOptionId(
    'exitcode.from.verdict',
    'Give the verdict of the test run as exit code',
    option_type=bool,
    default=False)

RUN_COMMAND_ENDPOINT = EndpointId('runcommand', """
    The K2 run command
    """)

PRE_INITIALIZE_SUT = MessageId(
    'PRE_INITIALIZE_SUT', """
    Triggered before the initialize the SUT.
    This message is sent once for each sut entity.

    data: None
    """)

INITIALIZE_SUT = MessageId(
    'INITIALIZE_SUT', """
    Triggered when the run command is ready to initialize the SUT.
    Initializing the SUT should done be as a callback.
    This message is sent once for each sut entity.

    data: None
    """)

POST_INITIALIZE_SUT = MessageId(
    'POST_INITIALIZE_SUT', """
    Triggered after the initialize the SUT.
    This message is sent once for each sut entity.

    data: None
    """)

UNINITIALIZE_SUT = MessageId(
    'UNINITIALIZE_SUT', """
    Triggered when run is ready to uninitialize the SUT.
    Uninitializing the SUT should done be as a callback.
    This message is sent once for each sut entity.

    data: None
    """)

PRE_TEST_RUN = MessageId(
    'PRE_TEST_RUN', """\
    Triggered before the test run is started.

    data: None
    """)

TEST_RUN = MessageId(
    'TEST_RUN', """\
    Triggered when the test run is started.

    data: None
    """)

POST_TEST_RUN = MessageId(
    'POST_TEST_RUN', """\
    Triggered when the test run is completed.

    data: None
    """)

GET_RUN_VERDICT = MessageId(
    'GET_RUN_VERDICT', """
    Request to get the verdict for a test run.
    Response should be a Verdict enum value.

    data: None
    """)

TestRunData = namedtuple('TestRunData', ['parent_scope'])


def run(core):
    """
    Run the specified test module.

    Example of running a specific test file::

        zk2 run path/to/test_file.py

    Example of running a specific test function in the file::

        zk2 run path/to/test_file.py:test_something

    Example of running a using the module name::

        zk2 run path.to.test_module
    """
    try:
        suts = core.config.get(SUT)

        for sut in suts:
            execute_sequence_point(PRE_INITIALIZE_SUT, core.messagebus, entity=sut)

        for sut in suts:
            execute_sequence_point(INITIALIZE_SUT, core.messagebus, entity=sut)

        for sut in suts:
            execute_sequence_point(POST_INITIALIZE_SUT, core.messagebus, entity=sut)

        test_run_data = TestRunData(core.session_scope)

        execute_sequence_point(PRE_TEST_RUN, core.messagebus, data=test_run_data)

        execute_sequence_point(TEST_RUN, core.messagebus, data=test_run_data)

        execute_sequence_point(POST_TEST_RUN, core.messagebus)

        for sut in suts:
            execute_sequence_point(UNINITIALIZE_SUT, core.messagebus, entity=sut)

        if core.config.get(EXIT_CODE_FROM_VERDICT):
            for verdict_future in core.messagebus.send_request(GET_RUN_VERDICT).wait(1):
                verdict = verdict_future.result()

                # Ugly check because import Verdict.PASSED leads to circular dependency
                if verdict.value > 0:
                    return 1
            return 0
    except Exception as e:
        msg = 'Run command failed due to exception: {msg}'.format(msg=str(e))
        logger.debug(msg, exc_info=True)
        logger.critical(msg)
        return 1

    return 0


def execute_sequence_point(message_id, messagebus, entity=None, data=None):
    """
    Execute a sequence point in the run sequence.

    :param name: the message_id defining the sequence poitn
    :param message_bus: the messagebus to send the message to
    :param data: message data
    """
    logger.debug('Executing sequence point {sequence_point}'.format(sequence_point=message_id.name))
    messagebus.trigger_event(message_id, RUN_COMMAND_ENDPOINT, entity=entity, data=data)


RUN_COMMAND = CommandId(
    'run', run.__doc__, run, [
        ConfigOption(EXIT_CODE_FROM_VERDICT, required=True),
    ], uses=['sut'])


@FrameworkExtension(
    name='runcommand',
    commands=[RUN_COMMAND],
    endpoints_and_messages={
        RUN_COMMAND_ENDPOINT: [
            PRE_INITIALIZE_SUT, INITIALIZE_SUT, POST_INITIALIZE_SUT, UNINITIALIZE_SUT, PRE_TEST_RUN,
            TEST_RUN, POST_TEST_RUN, GET_RUN_VERDICT
        ]
    })
class RunCommand(object):
    """Provides the run command."""

    def __init__(self, config, instances):
        pass
