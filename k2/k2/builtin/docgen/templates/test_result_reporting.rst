.. _test_result_reporting-label:

*********************
Test Result Reporting
*********************

Arguably one of the most familiar parts of K2 you will ever encounter is the
test result reporters. They are what render the test results to a readable
format.

There are two main test result reporters currently, the text reporter and the
TestNG reporter.

Text Reporter
=============

When developing K2 test cases and running the tests on the command line, the
:ref:`extension-textreport` addon is what displays test results.

A familiar example::

  Results (PASSED):
  -------
  systest.feature.run.lifetime.test_running_tests_that_uses_module_scope_component         PASSED  0:00:00.513112
  systest.feature.run.lifetime.test_running_tests_that_uses_class_scope_component          PASSED  0:00:00.502826
  systest.feature.run.lifetime.test_running_tests_that_uses_class_session_component        PASSED  0:00:00.528154
  systest.feature.run.lifetime.test_running_tests_that_yield_from_components               PASSED  0:00:00.490114
  systest.feature.run.lifetime.test_running_tests_that_uses_context_managers_as_components PASSED  0:00:00.497153
  systest.feature.run.lifetime.test_running_tests_that_override_component_default_scope    PASSED  0:00:00.491251

  Failures/Errors:
  ----------------

  Summary:
  --------
  Passed:  6
  Failed:  0
  Error:   0
  Pending: 0
  Skipped: 0
  Ignored: 0
  Total:   6
  Execution time: 0:00:03.138271

The text reporter shows you a list of all test cases that were executed along
with their verdicts and execution times, followed by a summary.

The text reporter will show tracebacks for failing test cases::

  Failures/Errors:
  ----------------
  systest.feature.example.test_something_that_fails
    Traceback (most recent call last):
      File "/k2/k2/runner/runner.py", line 285, in run_test_case
        current_test_case.run, scope, *args, **kwargs)
      File "/k2/.venv/lib/python3.6/site-packages/zaf/component/factory.py", line 104, in call
        return callable(*args, **kwargs)
      File "/k2/systest/feature/example.py", line 97, in test_something_that_fails
        assert False
    AssertionError

If you have chosen to view test case ownership information using the
:ref:`option-reports.text.show.owner` config option, the owner will be shown
next to the test case name for each failing test case::

  Failures/Errors:
  ----------------
  systest.feature.example.test_something_that_fails (Test case owner: Guild <guild@zenterio.com>)
    Traceback (most recent call last):
      File "/k2/k2/systest/feature/example.py", line 97, in test_something_that_fails
        assert False
    AssertionError


TestNG Reporter and Jenkins
===========================

When K2 tests run in Jenkins, the test reporting is done by the
:ref:`extension-testngreport` extension. It creates an XML report file that
conforms to the TestNG XML schema, which is then read by a Jenkins plugin to
display the results in the Jenkins job.

The Jenkins interface for the TestNG reports is fairly straightforward to
use. The basic point of entry is the results summary which directly links to
any failed test cases. (The **suite.suite** test failure is a K2-specific
detail required to capture internal K2 errors separately from test case
failures. It will always appear if some test case fails.)

.. image:: jenkins_summary.png

In the detailed view for a failed test case, you will see the most necessary
information such as the exception type and traceback. The test case owner is
shown as well if the test has an owner associated with it.

.. image:: jenkins_failure.png
