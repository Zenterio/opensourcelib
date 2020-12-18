"""
Dispatchers let you listen for events and requests on a messagebus, and call a handler method when they occur.

If several dispatchers are registered on the same message, they are called in order of priority, highest first.
"""
import abc
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import RLock, Thread

from .message import Message
from .messagebus import NoSuchDispatcher, NoSuchEndpoint, NoSuchMessage

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Dispatcher(metaclass=abc.ABCMeta):
    """A MessageBus dispatcher base class that fulfills the interface expected by the MessageBus."""

    def __init__(self, messagebus, priority=0):
        self._messagebus = messagebus
        self._priority = priority
        self._active_count = ActiveCount()
        self._component_factory = messagebus.component_factory
        self._scope = self._component_factory.enter_scope('dispatcher', messagebus.scope)

    def register(self, message_ids, endpoint_ids=None, entities=None, optional=False):
        """
        Register a dispatcher in the messagebus.

        The dispatcher is registered for the provided combination of message_ids,
        endpoint_ids and entities.

        By default, attempting to register a dispatcher on a message or endpoint that
        isn't defined is an error. Setting optional=True suppresses this error, allowing
        you to listen to events that may not be defined.
        """
        try:
            self._messagebus.register_dispatcher(self, message_ids, endpoint_ids, entities)
            self.start()
        except (NoSuchMessage, NoSuchEndpoint) as e:
            if optional is False:
                raise
            logger.debug('Ignoring optional dispatcher: {msg}'.format(msg=str(e)))

    def deregister(self, message_ids, endpoint_ids=None, entities=None):
        """
        Deregister the dispatcher from the messagebus.

        If the dispatcher no longer has any registrations stop() is called.
        """
        still_registered = self._messagebus.deregister_dispatcher(
            self, message_ids, endpoint_ids, entities)
        if not still_registered:
            self.stop()

    def destroy(self):
        """
        Deregister this dispatcher from the messagebus.

        This will call the stop method on subclasses.
        """
        try:
            self._messagebus.deregister_dispatcher(self)
        except NoSuchDispatcher:
            pass
        finally:
            self.stop()
            try:
                self._component_factory.exit_scope(self._scope)
            except Exception as e:
                logger.debug(str(e), exc_info=True)
                logger.error(str(e))

    def get_active_count(self):
        return self._active_count.active_count()

    def get_queue_count(self):
        return 0

    def start(self):
        pass

    def stop(self, timeout=None):
        pass

    @property
    def priority(self):
        return self._priority

    @abc.abstractmethod
    def dispatch(self, message):
        """
        Callable that will be registered to the messagebus and that will be triggered by message.

        :param message: the Message object
        """
        pass


class ThreadPoolDispatcher(Dispatcher):
    """
    A dispatcher that calls handle_message in a thread pool.

    This dispatcher has a pool of threads, allowing it to execute several handle_message at once.
    If all the threads are occupied, incoming messages are put in a queue.
    """

    def __init__(self, messagebus, handle_message, max_workers=None, priority=0):
        super().__init__(messagebus, priority)
        self._handle_message = handle_message
        self._max_workers = max_workers
        self._executor = None
        self._stopped = True

    def start(self):
        self._stopped = False
        self._executor = ThreadPoolExecutor(
            max_workers=self._max_workers
            if self._max_workers is not None else (os.cpu_count() or 1) * 5,
            thread_name_prefix='{name}-{id}-'.format(
                name=self.log_repr(), id=id(self._handle_message)))

    def stop(self, timeout=10):
        if self._executor is not None:
            self._executor.shutdown(wait=False)
        self._executor = None
        self._stopped = True

    def dispatch(self, message):
        logger.debug(
            "Adding message '{message_name}' to queue for '{handler}'".format(
                message_name=message.message_id.name, handler=self.log_repr()))

        self._executor.submit(self.execute_handle_message, message)

    def execute_handle_message(self, message):
        logger.debug(
            "Receiving message '{message_name}' in '{handler}'".format(
                message_name=message.message_id.name, handler=self.log_repr()))

        # wrap with component factory must be closest to the real handle_message to be able to read
        # the requires decorator from it
        wrapped_handle_message = wrap_with_component_factory(
            self._handle_message, self._component_factory, self._scope)

        wrapped_handle_message = wrap_with_active_count(wrapped_handle_message, self._active_count)
        wrapped_handle_message = wrap_with_exception_logging(
            wrapped_handle_message, self.log_repr())
        if message.future is not None:
            wrapped_handle_message = wrap_with_future(wrapped_handle_message)

        return wrapped_handle_message(message)

    def get_queue_count(self):
        return self._executor._work_queue.qsize()

    def log_repr(self):
        try:
            return '{module}.{qualname}'.format(
                module=self._handle_message.__module__, qualname=self._handle_message.__qualname__)
        except Exception:
            # Can fail if using a lambda as handle_message
            # This should be fixed with a better log_repr implementation
            # The exising one gives quite ugly and unreadable logs
            return 'unknown'


class SequentialDispatcher(ThreadPoolDispatcher):
    """
    Puts messages in a queue and sequentially calls handle_message.

    This dispatcher has its own thread, and if it is being used when a message is received, handle_message is queued.
    This ensures that messages are handled in the same order as they are received.
    """

    def __init__(self, messagebus, handle_message, priority=0):
        super().__init__(messagebus, handle_message, max_workers=1, priority=priority)


class CallbackDispatcher(Dispatcher):
    """
    A dispatcher that calls handle_message in the same thread as the message was sent from.

    This dispatcher essentially pauses execution of the message sender,
    ensuring that the message is handled before continuing.
    """

    def __init__(self, messagebus, handle_message, priority=0, wrap_with_thread=False):
        super().__init__(messagebus, priority)
        self._handle_message = handle_message
        self._wrap_with_thread = wrap_with_thread

    def dispatch(self, message):
        logger.debug(
            "Dispatching message '{message_name}' to '{handler}'".format(
                message_name=message.message_id.name, handler=self.log_repr()))
        # wrap with component factory must be closest to the real handle_message to be able to read
        # the requires decorator from it
        wrapped_handle_message = wrap_with_component_factory(
            self._handle_message, self._component_factory, self._scope)

        wrapped_handle_message = wrap_with_active_count(wrapped_handle_message, self._active_count)
        wrapped_handle_message = wrap_with_exception_logging(
            wrapped_handle_message, self.log_repr())
        if message.future is not None:
            wrapped_handle_message = wrap_with_future(wrapped_handle_message)
        if self._wrap_with_thread:
            wrapped_handle_message = wrap_with_thread(
                wrapped_handle_message, self.log_repr(), id(self._handle_message))

        wrapped_handle_message(message)

    def log_repr(self):
        try:
            return '{module}.{qualname}'.format(
                module=self._handle_message.__module__, qualname=self._handle_message.__qualname__)
        except Exception:
            # Can fail if using a lambda as handle_message
            # This should be fixed with a better log_repr implementation
            # The exising one gives quite ugly and unreadable logs
            return 'unknown'


class ConcurrentDispatcher(CallbackDispatcher):
    """
    A dispatcher that calls handle_message in a separate thread.

    This dispatcher starts a separate thread for the handle_message method,
    which means there's no guarantuee about when or in which order they are completed.
    """

    def __init__(self, messagebus, handle_message, priority=0):
        super().__init__(messagebus, handle_message, priority, wrap_with_thread=True)


def wrap_with_component_factory(handle_message, component_factory, parent_scope):

    def wrapped(message):
        message_scope = component_factory.enter_scope('message', parent_scope)
        try:
            fixated_entities = []
            if message.entity is not None:
                fixated_entities.append(message.entity)
            return component_factory.call(
                handle_message, message_scope, message, fixated_entities=fixated_entities)
        finally:
            component_factory.exit_scope(message_scope)

    return wrapped


def wrap_with_exception_logging(handle_message, handler_name):

    def wrapped(message):
        try:
            return handle_message(message)
        except Exception:
            logger.debug(
                "Error occured when handling message '{message}' in handler '{handler}'".format(
                    message=message.message_id.name, handler=handler_name),
                exc_info=True)
            raise

    return wrapped


def wrap_with_future(handle_message):

    def wrapped(message):
        message.future.run(handle_message, message)

    return wrapped


def wrap_with_thread(handle_message, dispatcher_name, id):

    def wrapped(message):
        thread = Thread(
            target=handle_message,
            args=[message],
            name='{name}-{id}'.format(name=dispatcher_name, id=id))
        thread.start()

    return wrapped


def wrap_with_active_count(handle_message, active_count):

    def wrapped(message):
        try:
            active_count.increase()
            return handle_message(message)
        finally:
            active_count.decrease()

    return wrapped


class ActiveCount(object):

    def __init__(self):
        self.lock = RLock()
        self._count = 0

    def increase(self):
        with self.lock:
            self._count += 1

    def decrease(self):
        with self.lock:
            self._count -= 1

    def active_count(self):
        return self._count


class QueueUnblockedException(Exception):
    pass


class LocalMessageQueue(object):
    """
    A MessageBus message handler that makes it easy to wait_for_not_active for messages.

    A basic example of using the LocalMessageQueue:

    .. code-block:: python

        #!python
        with LocalMessageQueue(messagebus, [message_id_1, message_id_2], [endpoint_id_1]) as q:
            # start stuff that will trigger messages
            message = q.get(timeout=5)

    The match callable can be used to filter the messages on message internal information:

    .. code-block:: python

        #!python
        def is_important(message):
            return something_important in message.data

        with LocalMessageQueue(messagebus, [message_id_1, message_id_2], [endpoint_id_1], match=is_important) as q:
            # start stuff that will trigger messages
            message = q.get(timeout=5)
            do_stuff(message.data[something_important])
    """

    def __init__(
            self, messagebus, message_ids, endpoint_ids=None, entities=None, match=None,
            priority=0):
        self._message_ids = message_ids
        self._endpoint_ids = endpoint_ids if endpoint_ids else []
        self._entities = entities
        self._match = match
        self._matching_messages = Queue()
        self._dispatcher = CallbackDispatcher(messagebus, self.handle_message, priority)

    def __enter__(self):
        self._dispatcher.register(self._message_ids, self._endpoint_ids, self._entities)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._dispatcher.destroy()

    def handle_message(self, message):
        if self._match is None or self._match(message):
            self._matching_messages.put(message)

    def get(self, timeout=None) -> Message:
        message = self._matching_messages.get(timeout=timeout)
        if message is None:
            raise QueueUnblockedException('Queue was unblocked before receiving next message')
        return message

    def get_nowait(self) -> Message:
        return self._matching_messages.get_nowait()

    def empty(self) -> bool:
        return self._matching_messages.empty()

    def clear(self):
        with self._matching_messages.mutex:
            self._matching_messages.queue.clear()

    def unblock(self):
        """
        Unblock the ongoing or next get call.

        This will make get raise a QueueUnblockedException.
        This is only meant to be used on a queue that won't be used anymore.
        """
        self._matching_messages.put(None)


class MessageFilter(object):
    """
    Can be used to filter an MessageDispatcher on internal information in the message object.

    This is useful when having general messages and only want the handle_message function to
    be triggered on some of them.

    .. code-block:: python

        #!python
        def match(message):
            return something_important in message.data

        @MessageFilter(match)
        def handle_message(message):
            do_stuff()
    """

    def __init__(self, match):
        self._match = match

    def __call__(self, handle_message):

        def wrapped_handle_message(message):
            if self._match(message):
                handle_message(message=message)

        return wrapped_handle_message
