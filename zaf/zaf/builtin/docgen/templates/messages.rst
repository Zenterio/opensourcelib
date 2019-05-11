The messages module
*******************

.. automodule:: zaf.messages


Messages
========

Zaf uses message handling based around a message bus and different kinds of message dispatchers.

A message has an identifier and carries some data. The message bus is then responsible for transporting
messages to their intended destination. The message bus supports two modes of sending messages, events
and requests. The recipients are identified by their endpoint and optionally their entities.

.. note::

  Events are sent from an endpoint, while requests are received by an endpoint.

The message bus supports two types of messages, requests and events.

.. automodule:: zaf.messages.messagebus
.. autoclass:: MessageBus
   :members:

Dispatchers
=====================

.. automodule:: zaf.messages.dispatchers

.. autoclass:: Dispatcher
   :members:

.. autoclass:: ThreadPoolDispatcher
   :members:

.. autoclass:: SequentialDispatcher
   :members:

.. autoclass:: ConcurrentDispatcher
   :members:

.. autoclass:: CallbackDispatcher
   :members:

.. autoclass:: LocalMessageQueue
   :members:


Dispatcher Decorators
=====================

.. automodule:: zaf.messages.decorator

.. autoclass:: DispatcherDecorator
   :members: