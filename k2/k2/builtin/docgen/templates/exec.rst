.. _exec-label:

**************
Exec component
**************

The exec component is used to execute shell commands on a SUT.
There are multiple implementations of this component using different transports.

Interface
=========

send_line:
    Sends a line and waits for the response

send_line_nowait:
    Sends a line but doesn't wait for response

.. toctree::
    :maxdepth: 1
    :caption: Variants:

    extensions/telnet
    extensions/zserial
    extensions/hostshellexec
