
.. _logging:

*******
Logging
*******

K2 uses the `Python standard library logging <https://docs.python.org/3.5/library/logging.html#module-logging>`_.

The conventions listed below should be respected by all core modules and extensions.

Log Levels
==========

K2 uses the built in log levels:

* Critical
* Error
* Warning
* Info
* Debug

See the respective sections below for how and in what context each level should be used.

Critical Level
--------------
Critical level should only be used to provide information about critical and unexpected
events that is non-recoverable. It signifies that the module/extension that
logged the message can not continue performing its function and need to shutdown
permanently.

Error Level
-----------
Error level should be used to provide information about unexpected errors
that the module/extension can not handle itself but can recover from in the sense
that it has not lost its primary function. So it is essentially the
same kind of problems that might be logged on critical level, with the distinction
that the module/extension can recover from it and still perform its function in
future calls.

Warning Level
-------------
Warning level should be used for messages about events that did not cause
a failure at this particular instance but signals a potential failure in the
future. This includes degraded performance, high usage close to max capacity,
large allocation of temporary resources, long response times, etc.

Info Level
----------
Info level should be used to provide status information that you would expect
to see from tools running in `verbose` mode. It provide information about the
process that can be informative to an outside spectator.

A module triggered by unpredictable outside interaction should log each new
interaction on info level. This include handling a new request or spawning of a
new worker thread to perform the modules primary duties.

Higher level modules that consists of multiple steps can log each step to indicate
progress and provide additional context.

Debug
-----
The debug level should be used for module/extension internal information that
can assist in debugging the module/extension from a coding defect perspective,
to discover anomalies in value input/output or to assist in performance trouble
shooting.

Module input values (and output if manipulated along the way) can be logged if
of reasonable size and frequency. If the data itself is too large to log, some
meta data about the data such as size and SHA can be recorded instead.

Examples
========
A data-store that can't access the underlying database due to incorrect credentials
will most likely never be given access and can hence not perform its function.
This should be logged at `critical` level.

In contrast, if one database call out a thousand fails due to temporary
overload of the database server, it is not critical in the sense that data-store
functionality have been lost indefinitely. It should be logged as an `error`.

If the database connection is known to be unstable and the data-store has a built-in
back-off-try-again mechanism each such failed attempt should probably treated as a
`warning` while the decision to stop retrying should be logged as an `error`.
Enough subsequent errors might trigger a decision that the data-store can no longer
reliably store its data, resulting in a `critical` message.

A math division function will fail at division by zero, but the division function
can still perform division in general, and is hence not a critical event. It
should be logged as an `error`.

A data-store that receives a slow response from the database, the response taking
longer than a threshold but still completes, should be logged as a `warning` since
the problem did not cause a failure in function, but risk turning into one if the
slow response time gets worse. Slow response time might also signal poor end-user
experience that warrants a warning.

A random number generator should write a `warning` if the entropy is close to being
insufficient to produce random enough values. It should log an `error` if entropy
is insufficient after time-out has elapsed. The lacking of an entropy source
constitutes a `critical` problem.

A high level function comprised of several steps should log the beginning (and possibly end)
of each step on `info` level to show its progress and to provide additional context.

An authentication module accepting login credentials from an external party should
log the event on `info` level due to it being an external request that can not be
predicted and the operation is the main function of the module.

A tool to flash embedded devices with new firmware can log a message on `info` level
for each new invocation, including the device ID and the firmware version if known.

Each data-store transaction, including the request parameters (and the data retrieved
if it is of reasonable size, otherwise the data size) can be logged on `debug` level.

Each message dispatched on a message bus, including the meta data (and the actual message
if it is of reasonable size, otherwise the data size) can be logged on `debug` level.
