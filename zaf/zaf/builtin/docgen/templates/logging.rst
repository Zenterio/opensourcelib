*******
Logging
*******

{{application_name|capitalize}} supports logging in different ways using multiple different extensions.
It's based on the Python logging concepts loggers and handlers.
A logger is a *source* for log messages and a handler is a *sink* for log messages.

The built-in functionality supports the following different types of handlers.

* Command line
* File

Log Levels
==========

The log levels that can be used when configuring the different loggers are

* off
* debug
* info
* warning
* error

Command line
============

The following config options can be used to configure the command line logging.

:ref:`option-log.level`:
    Sets the log level on the command line log handler

:ref:`option-log.format`:
    Sets the log format on the command line log handler.
    The format is using the standard python log format.
    See `Formatter <https://docs.python.org/3/library/logging.html#formatter-objects>`_ and `LogRecord <https://docs.python.org/3/library/logging.html#logrecord-objects>`_ for more information.

:ref:`option-log.dir`:
    Sets the log dir value. Default is '${output.dir}/logs.
    This needs to be referenced in the log file path to be used.

:ref:`option-log.debug`:
    Loggers that should be logged on debug level to the command line handler.

:ref:`option-log.info`:
    Loggers that should be logged on info level to the command line handler.

:ref:`option-log.warning`:
    Loggers that should be logged on warning level to the command line handler.

:ref:`option-log.error`:
    Loggers that should be logged on error level to the command line handler.

{% if application_context == 'EXTENDABLE' %}
Extensions
==========

The log configuration for extensions configures the actual loggers connected to that extension.
Setting the log level for an extension means that no messages on a lower level will be sent to any of the handlers.

:ref:`option-ext.<enabled>.log.level`:
    Sets the log level for an enabled extension.
{% endif %}

Log files
=========

Log files can be configured by configuring which loggers that should be sent to each file and the log level for the file.
To create a log file the id of the file needs to be added to the *log.files.ids* config option.
Then the log file can be configured with the following config options.

:ref:`option-log.file.<ids>.enabled`:
    Default true, but this can be used to disable a log file without removing the config for it.

:ref:`option-log.file.<ids>.path`:
    The path to the log file.
    It is useful to refer to the log.dir config when configuring the log.file.path using a path like '${log.dir}/logfile.log'

:ref:`option-log.file.<ids>.loggers`:
    List of loggers that should be sent to the file.

:ref:`option-log.file.<ids>.log.level`:
    The log level for the file. Can be overridden by the extension logger configuration.

:ref:`option-log.file.<ids>.format`:
    The log message format used in the file. See log.format for more information.

:ref:`option-log.file.<ids>.debug`:
    Loggers that should be logged on debug level to the file.

:ref:`option-log.file.<ids>.info`:
    Loggers that should be logged on info level to the file.

:ref:`option-log.file.<ids>.warning`:
    Loggers that should be logged on warning level to the file.

:ref:`option-log.file.<ids>.error`:
    Loggers that should be logged on error level to the file.


Rotating log files
------------------

Log files can be configured to rotate on *scope* changes.
This means that every time a scope is entered a new file will be created.
A common use case for this is to create log files for each test case.

Scopes are defined by extensions and are defined as strings.
Scopes can also report a result at the exit of the scope that can be used to determine if the log file for the scope should be kept or not.
Name of results are defined by the extension that defines the scope and is not standardized.

Rotating log files can be configured with the following config options.

:ref:`option-log.file.<ids>.rotate.scope`:
    The id of the scope to rotate the log file on.

:ref:`option-log.file.<ids>.rotate.deleteforresults`:
    List of results for which the the rotated log file should be deleted.

Rotating log files need to know how to name the files and to do that the *log.file.<file_id>.path* needs to include a '{scope}' variable that will be filled in with the scope name.


{% for l in custom_logging_items %}
.. include:: ./{{l}}
{% endfor %}

Examples
========

Configuring default log level on command line
---------------------------------------------

.. code-block:: shell

    > {{entrypoint_name}} --log-level info <command>


Configuring log level for a specific logger on command line
-----------------------------------------------------------

.. code-block:: shell

    > {{entrypoint_name}} --log-debug testcase <command>



Configuring log level for a specific extension on command line
--------------------------------------------------------------

.. code-block:: shell

    > {{entrypoint_name}} --ext-<extension_name>@log.level debug <command>


Configuring extension log levels using config file
--------------------------------------------------
.. code-block:: yaml

    log.level: debug
    log.format: "%(message)s"
    ext.<extension_name1>.log.level: warning
    ext.<extension_name2>.log.level: error


Configuring log file using config file
--------------------------------------

.. code-block:: yaml

    log.file.ids: [myfile]
    log.file.myfile.path: ${log.dir}/myfile.log
    log.file.myfile.loggers: [testrunner, myextension]
    log.file.myfile.log.level: debug
    log.file.myfile.format: "%(message)s"

Configuring rotating log file using config file
-----------------------------------------------

.. code-block:: yaml

    log.file.ids: [myrotatingfile]
    log.file.myrotatingfile.path: ${log.dir}/tests/myrotatingfile_{scope}.log
    log.file.myrotatingfile.loggers: [testrunner, myotherextension]
    log.file.myrotatingfile.log.level: info
    log.file.myrotatingfile.format: "%(message)s"
    log.file.myrotatingfile.rotate.scope: testcase
    log.file.myrotatingfile.rotate.deleteforresults: [PASSED, SKIPPED, IGNORED]
