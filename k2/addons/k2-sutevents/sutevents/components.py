import logging
import re
from contextlib import contextmanager
from queue import Empty

from zaf.component.decorator import component, requires
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.dispatchers import LocalMessageQueue
from zaf.utils.future import Future

from k2.cmd.run import RUN_COMMAND
from k2.sut import SUT_RESET_DONE, SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED, SUT_RESET_STARTED
from k2.sut.log import SUT_LOG_SOURCES, NoLogSources
from sutevents import IS_SUT_RESET_EXPECTED, LOG_LINE_RECEIVED, SUTEVENTSCOMPONENT_ENDPOINT

logger = logging.getLogger(get_logger_name('k2', 'sutevents.components'))


class NoMatchingLogLine(AssertionError):
    pass


class SutEventTimeout(Exception):
    pass


@requires(sut='Sut')
@requires(config='Config')
@requires(messagebus='MessageBus')
@component(name='SutEvents', provided_by_extension='sutevents')
class SutEvents(object):
    """
    Component for listening for SUT-related events.

    Simplifies listening or otherwise acting on events related to the SUT.
    """

    def __init__(self, messagebus, config, sut):
        self._messagebus = messagebus
        self._sut = sut
        self._log_entities = config.get(SUT_LOG_SOURCES, entity=sut.entity)

    def is_sut_reset_expected(self):
        """Check if a sut reset is expected for the sut right now."""
        return self._messagebus.send_request(
            IS_SUT_RESET_EXPECTED, entity=self._sut.entity).wait()[0].result()

    @contextmanager
    def wait_for_log_line(self, log_line_regex, log_sources=None):
        """
        Context manager that can be used to wait for log lines matching a specific regex.

        Every call to get returns the next matching log lines represented by a regex Match object.
        See `Match Objects <https://docs.python.org/3/library/re.html#match-objects>`_ for more information.

        By default, all available log sources are sourced for the expected log line. Use log_sources
        to filter what log sources should be used. The specified log source still needs to be defined
        for the sut.

        Example of how this can be used

        .. code-block:: python

            @requires(sut_events='SutEvents')
            def test_case(sut_events):
                with sut_events.wait_for_log_line(r'(?P<named_match>regex) [M]atching log lines') as matches:
                    do_stuff_that_generates_log_lines()
                    match = matches.get(timeout=1)
                    assert match.groupdict()['named_match'] == 'regex'
                    line = match.string
        """
        logger.debug('Waiting for logline {regex}'.format(regex=log_line_regex))
        compiled_regex = re.compile(log_line_regex)

        if not self._log_entities:
            msg = 'No log sources available for {sut}'.format(sut=self._sut.entity)
            logger.error(msg)
            raise NoLogSources(msg)

        if log_sources is not None:
            log_entities = log_sources if isinstance(log_sources, list) else [log_sources]
            for entity in log_entities:
                if entity not in self._log_entities:
                    msg = '{source} is not among the available log sources for {sut}'.format(
                        source=entity, sut=self._sut.entity)
                    logger.error(msg)
                    raise NoLogSources(msg)
        else:
            log_entities = self._log_entities

        def match(message):
            return compiled_regex.search(message.data) is not None

        with LocalMessageQueue(self._messagebus, [LOG_LINE_RECEIVED], entities=log_entities,
                               match=match) as queue:

            class QueueWrapper(object):

                def __init__(self, queue):
                    self._queue = queue

                def get(self, timeout=None):
                    """
                    Return a regex match object for the next matching line.

                    match.string can be used to retrieve the full line

                    :param timeout: The timeout in seconds to wait for next line
                    """
                    try:
                        log_line_message = self._queue.get(timeout=timeout)
                        logger.debug('log line matched: {data}'.format(data=log_line_message.data))
                        return compiled_regex.search(log_line_message.data)
                    except Empty:
                        msg = "No log line received matching '{regex}'".format(regex=log_line_regex)
                        logger.debug(msg)
                        raise NoMatchingLogLine(msg) from None

                def get_all(self):
                    """
                    Return a list of regex match objects for the matching lines so far.

                    This function does not block.
                    """
                    result = []
                    try:
                        while True:
                            log_line_message = self._queue.get_nowait()
                            match = compiled_regex.search(log_line_message.data)
                            result.append(match)
                    except Empty:
                        pass
                    return result

            yield QueueWrapper(queue)

    def wait_for_log_line_all(self, log_line_regex):
        """Wait for a log line on all available log sources."""
        return self.wait_for_log_line(log_line_regex)

    @contextmanager
    def expect_reset(self):
        """
        Context manager that send :ref:`message-SUT_RESET_EXPECTED` and :ref:`message-SUT_RESET_NOT_EXPECTED`.

        This should be used when triggering an expected sut reset so that extensions
        monitoring the SUT doesn't report errors and can deal with the reset.

        Example of how this can be used

        .. code-block:: python

            @requires(sut_events='SutEvents')
            def test_case(sut_events):
                with sut_events.expect_reset():
                    do_stuff_that_triggers_reset()
        """
        try:
            logger.debug('Expect reset for sut {entity}'.format(entity=self._sut.entity))
            self._messagebus.trigger_event(
                SUT_RESET_EXPECTED, SUTEVENTSCOMPONENT_ENDPOINT, entity=self._sut.entity)
            yield
        finally:
            self._messagebus.trigger_event(
                SUT_RESET_NOT_EXPECTED, SUTEVENTSCOMPONENT_ENDPOINT, entity=self._sut.entity)
            logger.debug('Do not expect reset for sut {entity}'.format(entity=self._sut.entity))

    @contextmanager
    def await_sut_message(self, message_id, timeout=300):
        """
        Context manager that can be used to wait for a SUT event.

        The context manager yields a future that will contain the sut message.

        Example of how this can be used:

        .. code-block:: python

            @requires(sut_events='SutEvents')
            def test_case(sut_events):
                with sut_events.await_sut_message(SUT_RESET_EXPECTED) as future:
                    do_stuff_that_triggers_reset()

                do_stuff_after_reset_expected_has_been_received()
                sut_reset_expected_message = future.result()

        :param message_id: the ID of the message to wait for
        :param timeout: the timeout
        :return: future containing the message representing the sut event
        """
        logger.debug(
            'Await message {id} for sut {entity}'.format(id=message_id, entity=self._sut.entity))

        def wait_for_message(queue):
            try:
                return queue.get(timeout=timeout)
            except Empty:
                raise SutEventTimeout(
                    'Timeout when waiting for message {message_id} for sut {sut}'.format(
                        message_id=message_id, sut=self._sut.entity))

        with LocalMessageQueue(self._messagebus, [message_id],
                               entities=[self._sut.entity]) as queue:
            future = Future()
            yield future
            future.run(wait_for_message, queue)
            future.result(timeout=timeout)

    @contextmanager
    def await_sut_reset_started(self, timeout=None):
        """
        Asynchronous wait for :ref:`message-SUT_RESET_STARTED`.

        Exiting the context will block until the event has occured, or
        until timeout. SutEventTimeout exception is raised when the timeout occures.

        .. code-block:: python

            with sut_events.await_sut_reset_started(timeout=5):
                # action that will trigger SUT_RESET_STARTED.

        :param timeout: timeout in seconds
        """
        if timeout is None:
            timeout = self._sut.reset_started_timeout

        logger.debug('Await sut reset started')
        with self.await_sut_message(SUT_RESET_STARTED, timeout=timeout) as future:
            yield future

    @contextmanager
    def await_sut_reset_done(self, timeout=None):
        """
        Asynchronous wait for :ref:`message-SUT_RESET_DONE`.

        Exiting the context will block until the event has occured, or
        until timeout. SutEventTimeout exception is raised when the timeout occures.

        .. code-block:: python

            with sut_events.await_sut_reset_done(timeout=5):
                # action that will trigger SUT_RESET_DONE.

        :param timeout: timeout in seconds
        """
        if timeout is None:
            timeout = self._sut.reset_done_timeout

        logger.debug('Await sut reset done')
        with self.await_sut_message(SUT_RESET_DONE, timeout=timeout) as future:
            yield future


@CommandExtension(
    name='sutevents',
    extends=[RUN_COMMAND],
    config_options=[],
    endpoints_and_messages={
        SUTEVENTSCOMPONENT_ENDPOINT: [SUT_RESET_EXPECTED, SUT_RESET_NOT_EXPECTED]
    })
class SutEventsComponentExtension(AbstractExtension):
    """Provides the sutevents component."""

    def __init__(self, config, instances):
        pass
