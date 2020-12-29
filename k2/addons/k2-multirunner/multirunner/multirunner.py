"""
Simplified alternative to the standard test runner.

Sends a TEST_RUN_STARTED request and expects k2.runner.testcase.Verdict in
response. The responses are combined into a single verdict which is then
communicated by triggering a TEST_RUN_FINISHED event once all reponses have
been collected.
"""
from datetime import datetime

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension
from zaf.messages.decorator import callback_dispatcher

from k2.cmd.run import RUN_COMMAND_ENDPOINT, TEST_RUN
from k2.finder.testfinder import RUN_COMMAND
from k2.results.results import TestRunFinished, TestRunStarted
from k2.runner import RUNNER_SUITE_NAME, TEST_CASE_FINISHED, TEST_CASE_SKIPPED, TEST_CASE_STARTED, \
    TEST_RUN_FINISHED, TEST_RUN_STARTED
from k2.runner.testcase import Verdict

from . import MULTI_RUNNER_ENABLED, MULTI_RUNNER_ENDPOINT, TEST_SUBRUN


@CommandExtension(
    name='multirunner',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(MULTI_RUNNER_ENABLED, required=True),
        ConfigOption(RUNNER_SUITE_NAME, required=True),
    ],
    endpoints_and_messages={
        MULTI_RUNNER_ENDPOINT: [
            TEST_SUBRUN,
            TEST_RUN_STARTED,
            TEST_RUN_FINISHED,
            TEST_CASE_STARTED,
            TEST_CASE_FINISHED,
            TEST_CASE_SKIPPED,
        ]
    },
    activate_on=[MULTI_RUNNER_ENABLED],
    default_enabled=False,
    replaces=['testrunner', 'testscheduler', 'testfinder'],
)
class MultiRunner(AbstractExtension):

    def __init__(self, config, instances):
        self._suite_name = config.get(RUNNER_SUITE_NAME)

    @callback_dispatcher([TEST_RUN], [RUN_COMMAND_ENDPOINT])
    @requires(messagebus='MessageBus')
    def run(self, message, messagebus):
        test_run_started = TestRunStarted(self._suite_name, datetime.now())
        messagebus.trigger_event(TEST_RUN_STARTED, MULTI_RUNNER_ENDPOINT, data=test_run_started)

        run_verdicts = messagebus.send_request(
            TEST_SUBRUN, MULTI_RUNNER_ENDPOINT, data=test_run_started)

        run_verdict = Verdict.PASSED
        for verdict in map(lambda future: future.result(), run_verdicts.as_completed()):
            if verdict is not None:
                run_verdict = run_verdict.combine(verdict)

        messagebus.trigger_event(
            TEST_RUN_FINISHED,
            MULTI_RUNNER_ENDPOINT,
            data=TestRunFinished(datetime.now(), run_verdict, ''))
