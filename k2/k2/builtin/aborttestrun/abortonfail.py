"""
Abort test run on first occurrence of something interesting.

Sometimes during development and troubleshooting (or to quickly deem a test run as failed), it can be
useful to abort the test run on first occurrence of something interesting.

Abort on failed test
====================

A test run will abort on the first failed test case. The rest of the test cases in the
test suite will be listed as _skipped_. This will also break looping of tests on first error.
This is enabled with the :ref:`option-abort.on.fail` option.

Abort on unexpected SUT reset
=============================

A test run will abort on the first unexpected SUT reset. The ongoing test case will be interrupted and the rest
of the test cases in the test suite will be listed as _skipped_.
This is enabled with the :ref:`option-abort.on.unexpected.sut.reset` option.
"""
import logging

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from k2 import ABORT
from k2.cmd.run import RUN_COMMAND
from k2.runner import TEST_CASE_FINISHED
from k2.runner.testcase import Verdict

from . import ABORT_ON_FAIL_ENABLED, ABORT_ON_FAIL_ENDPOINT

logger = logging.getLogger(get_logger_name('k2', 'aborttestrun'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='aborttestrun',
    extends=[RUN_COMMAND],
    config_options=[ConfigOption(ABORT_ON_FAIL_ENABLED, required=True)],
    endpoints_and_messages={ABORT_ON_FAIL_ENDPOINT: [ABORT]},
    activate_on=[ABORT_ON_FAIL_ENABLED])
class AbortOnFail(AbstractExtension):
    """
    Aborts test run on failed test functionality.

    Listens to the message TEST_CASE_FINISHED and looks at the test
    case's Verdict if the test case passed or failed. If the test case failed (verdict was FAILED or ERROR),
    AbortOnFail will send an ABORT message, which aborts the execution of the test run.

    """

    def __init__(self, config, instances):
        pass

    @callback_dispatcher([TEST_CASE_FINISHED])
    @requires(messagebus='MessageBus')
    def handle_test_case_finished(self, message, messagebus):
        if message.data.verdict in [Verdict.FAILED, Verdict.ERROR]:
            messagebus.trigger_event(ABORT, ABORT_ON_FAIL_ENDPOINT)
