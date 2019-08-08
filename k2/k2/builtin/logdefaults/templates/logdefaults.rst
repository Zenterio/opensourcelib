:ref:`extension-logdefaults`
============================

There is an extension that provides a default log configuration suited for running tests with the run command.
This makes the console log slightly less verbose, and puts a complete log as well as individual logs per extension in the log directory.
It also creates a log per test case and a testcase.log file with everything logged using the *testcase* logger.


:ref:`option-logdefaults.enabled`:
    If true, the extension configures logging
