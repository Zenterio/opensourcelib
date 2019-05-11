"""
Provides decorators that can be used to automatically set up message dispatchers.

The purpose of these decorators is to provide a short-hand for defining dispatchers and avoid most
of the boilerplate code associated with setting up dispatchers.


Example:

.. code-block:: python

    # Simple extension with a single dispatcher, set up manually:
    class MyExtension(AbstractExtension):

        def  __init__(self, config, instances):
            self._entity = instances[CONFIG_OPTION]
            self._dispatcher = None

        def register_dispatchers(self, messagebus):
            self._dispatcher = SequentialDispatcher(messagebus, self.receive_message)
            self._dispatcher.register([MESSAGE_ID], [ENDPOINT_ID], entity=self._entity)

        def receive_message(self, message):
            do_stuff(message)

        def destroy(self):
            if self._dispatcher is not None:
                self._dispatcher.destroy()
            self._dispatcher = None

    # Simple extension with a single dispatcher, using decorators.
    class MyExtension(AbstractExtension):

        @sequential_dispatcher([MESSAGE_ID], [ENDPOINT_ID], entity=CONFIG_OPTION)
        def receive_message(self, message):
            do_stuff(message)


The two examples above are functionally equivalent, with the caveat that when using the decorator
the resulting dispatcher object is owned by the extension manager and can not easily be accessed
from an extension instance.

Both methods of setting up dispatchers may be combined in a single extension.
"""
import inspect

from .dispatchers import CallbackDispatcher, ConcurrentDispatcher, SequentialDispatcher, \
    ThreadPoolDispatcher


class DispatcherDescriptor(object):
    """Store information about how a dispatcher should be set up for a method."""

    def __init__(
            self,
            dispatcher_constructor,
            message_ids,
            endpoint_ids,
            entity_option_id=None,
            optional=False,
            max_workers=None,
            priority=0):
        self.dispatcher_constructor = dispatcher_constructor
        self.message_ids = message_ids
        self.endpoint_ids = endpoint_ids
        self.entity_option_id = entity_option_id
        self.optional = optional
        self.max_workers = max_workers
        self.priority = priority
        self.entity = None
        self.active = True


class DispatcherDecorator(object):
    """
    Decorate a method with information about what dispatchers should be set up.

    Information about each dispatcher is stored as the '_zaf_dispatcher_descriptors'
    property on the decorated method. The property is either not available or contains
    a list of what dispatchers to set up for the decorated method.

    If a dispatcher is declared optional, it will be registered only if the messages
    and endpoints that it dispatches are defined.

    All dispatchers have a priority, default 0, that allows you to specify dispatchers that should
    be called early or late when handling a message. Higher means earlier, and negative numbers are allowed.

    The max_workers parameter is only applicable for the threadpool_dispatcher decorator.
    It can be either a number or a ConfigOptionId that the extension uses.
    """

    def __init__(self, dispatcher_constructor):
        self._dispatcher_constructor = dispatcher_constructor

    def __call__(
            self,
            message_ids,
            endpoint_ids=None,
            entity_option_id=None,
            optional=False,
            max_workers=None,
            priority=0):

        def _decorator(function):
            _validate_function_argument(function)
            dispatcher_descriptor = DispatcherDescriptor(
                self._dispatcher_constructor, message_ids, endpoint_ids, entity_option_id, optional,
                max_workers, priority)
            try:
                function._zaf_dispatcher_descriptors.append(dispatcher_descriptor)
            except AttributeError:
                function._zaf_dispatcher_descriptors = [dispatcher_descriptor]
            return function

        return _decorator


sequential_dispatcher = DispatcherDecorator(SequentialDispatcher)
callback_dispatcher = DispatcherDecorator(CallbackDispatcher)
concurrent_dispatcher = DispatcherDecorator(ConcurrentDispatcher)
threadpool_dispatcher = DispatcherDecorator(ThreadPoolDispatcher)


def get_dispatcher_descriptors(extension):
    """
    Find all dispatcher descriptors associated with an extension.

    :return: A list of tuples containing methods and their associated dispatcher descriptor.
    """
    return [
        (method, dispatcher_descriptor)
        for _, method in inspect.getmembers(extension, inspect.ismethod)
        if hasattr(method, '_zaf_dispatcher_descriptors')
        for dispatcher_descriptor in method._zaf_dispatcher_descriptors
    ]


def _validate_function_argument(function):
    if not callable(function):
        raise TypeError("The 'function' argument of sequential_dispatcher() must be callable.")
