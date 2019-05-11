Blocker
*******

To effectively systest K2 it is sometimes needed to inject delays into the K2 execution.
The blocker is one way to stop the K2 execution at a specific event by adding a dispatcher to the message
that blocks until told to stop.

The blocker can either be configured using messages or using the *systest_plugins/blocker* plugin.

How it works
============

The blocker works by first registering a message to block by sending a START_BLOCKING_ON_MESSAGE request
with a StartBlockingInfo as message data.
This request returns an ID that should be used as the entity in later messages.

When the message that should be blocked on is triggered a BLOCKING_STARTED event is sent with entity=ID.

To stop the blocking a STOP_BLOCKING_ON_MESSAGE request should be sent.

When the blocking finishes either a BLOCKING_COMPLETED or a BLOCKING_TIMED_OUT will be sent with entity=ID.


Blocker
=======

.. autoclass:: zaf.builtin.blocker.blocker.Blocker
    :members:



Systest Component
=================

The systest component can also be used to configure the blocking.
It requires a RemoteClient to work by communicating between K2 processes.

Example of how to use it
------------------------

.. code-block:: python

    with SystestBlocker(MESSAGE_TO_BLOCK_ON, ENDPOINT, entity, timeout=5, remote=remote_client) as blocker:

        # Wait for the blocking to be started
        blocker.wait_for_started(timeout=1)

        # do stuff

        # Tell blocker to stop blocking
        blocker.stop_blocking()

        # Wait for the blocking to be finished. Returns a boolean if blocking was successful or timed out.
        successful = blocker.wait_for_finished()
