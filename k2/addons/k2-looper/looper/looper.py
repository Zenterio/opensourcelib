"""
Addon to configure looping of test cases, either by runtime or number of loops.

Only one of duration and repeats is allowed. This addon does not handle the case where
the initial scheduling of all included test cases exceeds the specified duration, it only
handles scheduling them again if it doesn't.
"""

import itertools
import logging
import time

from zaf.config import MutuallyExclusiveConfigOptions
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.dispatchers import CallbackDispatcher

from k2.cmd.run import RUN_COMMAND
from k2.runner import TEST_RUN_STARTED
from k2.scheduler import ADD_TEST_CASES, RUN_QUEUE_EMPTY, RUN_QUEUE_INITIALIZED, SCHEDULER_ENDPOINT
from k2.utils.timestring import parse_time
from looper import LOOP_DURATION, LOOP_REPEATS

logger = logging.getLogger(get_logger_name('k2', 'looper'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='looper',
    extends=[RUN_COMMAND],
    config_options=[
        ConfigOption(LOOP_DURATION, required=False),
        ConfigOption(LOOP_REPEATS, required=False),
    ])
class Looper(AbstractExtension):
    """Repeats test case executions to meet duration or repetition configuration."""

    def __init__(self, config, instances):
        self._loopduration = parse_time(config.get(LOOP_DURATION))
        self._looprepeats = config.get(LOOP_REPEATS)
        if self._loopduration and self._looprepeats:
            raise MutuallyExclusiveConfigOptions(
                'schedule.duration and schedule.repeats cannot be combined')
        self._messagebus = None
        self._run_queue_empty_dispatcher = None
        self._test_run_started_dispatcher = None
        self._run_queue_initialized_dispatcher = None
        self._original_run_queue = None
        self._cycle_run_queue = None
        self._start_time = None

    def register_dispatchers(self, messagebus):
        self._messagebus = messagebus
        if self._loopduration or self._looprepeats:
            self._run_queue_initialized_dispatcher = CallbackDispatcher(
                messagebus, self.handle_initialized)
            self._run_queue_initialized_dispatcher.register([RUN_QUEUE_INITIALIZED])
        if self._loopduration:
            self._test_run_started_dispatcher = CallbackDispatcher(messagebus, self.handle_started)
            self._test_run_started_dispatcher.register([TEST_RUN_STARTED])
            self._run_queue_empty_dispatcher = CallbackDispatcher(messagebus, self.handle_empty)
            self._run_queue_empty_dispatcher.register([RUN_QUEUE_EMPTY])

    def destroy(self):
        if self._run_queue_empty_dispatcher:
            self._run_queue_empty_dispatcher.destroy()
        if self._run_queue_initialized_dispatcher:
            self._run_queue_initialized_dispatcher.destroy()
        if self._test_run_started_dispatcher:
            self._test_run_started_dispatcher.destroy()

    def handle_initialized(self, message):
        self._original_run_queue = message.data
        self._cycle_run_queue = itertools.cycle(message.data)
        if self._looprepeats:
            self.schedule_repeats()

    def handle_started(self, message):
        self._start_time = time.time()

    def schedule_repeats(self):
        if self._looprepeats > 1:
            self._messagebus.send_request(
                ADD_TEST_CASES,
                SCHEDULER_ENDPOINT,
                data=self._original_run_queue * (self._looprepeats - 1)).wait()

    def handle_empty(self, message):
        if time.time() - self._start_time < self._loopduration:
            self._messagebus.send_request(
                ADD_TEST_CASES, SCHEDULER_ENDPOINT, data=[next(self._cycle_run_queue)]).wait()
