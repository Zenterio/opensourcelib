**********
Test Cases
**********

A test case is currently defined as any function that has a name that starts with *test_*.
The idea is to change this in the future to allow for standardized description and other metadata.

A test case can use :ref:`components` to inject functionality.
This allows for writing test cases towards abstractions instead of having too much details in the test case.


Verdicts
========

When running a test case it can result in many different verdicts.
This is used to communicate in more detail than just pass/fail what has happened.

PASSED:
    The test case was successful in verifying that the intended functionality works.

FAILED:
    A fault in the SUT stopped the test case from being successful.

ERROR:
    An error occurred outside of the functionality that the test was intended to verify.
    This can be a fault in the SUT, in K2 or in the surrounding environment.

PENDING:
    The test case has not been completed yet.

SKIPPED:
    The test case was not executed due to missing functionality.

IGNORED:
    The test case was not executed due to configuration, for example being disabled.


Ownership
=========

K2 supports annotating test case results with ownership information. The test
case owner is usually the person or guild responsible for the test case itself
or the subsystem under test, a responsibility which comes with a vested
interest in ensuring that the test case and its associated subsystem is
functioning correctly.

The reporting of test case ownership simplifies action when a test case fails
in e.g. Jenkins, by displaying the first point of contact for that particular
test case.

Currently, test case ownership is only reported by the :ref:`extension-jasmine`
extension.

To learn more about how to find the ownership information in K2's test result
reporting, please see the :ref:`test_result_reporting-label` chapter of the
user guide.


Disabling Test Cases
====================

Test cases can be disabled by using the @disabled decorator.
The test case will be included in the test reports with the IGNORED verdict.
For reporters that don't have an IGNORED verdict this will be mapped to SKIPPED or filtered out.

.. code-block:: python

    from k2.runner.decorator import disabled

    @disabled('A message describing why the test case is disabled')
    test_something():
        ...


Test Case Selection
===================

Test cases are selected in two steps.
The first step is to find and load test cases in the :ref:`extension-testfinder` using the :ref:`option-test.sources`
config option.
Then the selection is pruned in the :ref:`extension-testscheduler` using the
:ref:`option-tests.include`,
:ref:`option-tests.include.regex`,
:ref:`option-tests.exclude`,
:ref:`option-tests.exclude.regex`,
config options.

The normal use case is to give the test case root directory as :ref:`option-test.sources`
and then use the include and exclude options to make the more detailed selection.

The include and exclude options use the syntax 'package[.module[[.class].testcase]]' to let you include/exclude whole
or part of packages, modules, classes (if any) and test cases.

Examples on command line
------------------------

Select one test case ::

    zk2 run root/path/to/test/cases --tests-include package.module.class.test_my_test

Select two test cases ::

    zk2 run root/path/to/test/cases \
    --tests-include package.module.class.test_my_test \
    --tests-include package.module.class.test_my_test2

Select all test cases in class ::

    zk2 run root/path/to/test/cases \
    --tests-include package.module.class

Select all test cases in module ::

    zk2 run root/path/to/test/cases \
    --tests-include package.module

Select test cases with regex::

    zk2 run root/path/to/test/cases \
    --tests-include-regex '.*my_test.*'

Exclude all test cases with *stability* in the name with regex

    zk2 run root/path/to/test/cases \
    --tests-exclude-regex '*.stability.*'

Combination of include and exclude::

    zk2 run root/path/to/test/cases \
    --tests-include-regex '*.media.*' \
    --tests-exclude-regex '*.igmp.*' \
    --tests-exclude 'package.module.test_case_that_is_not_working_on_my_box

Example using config file
--------------------------

.. code-block:: yaml

    test.sources: [root/path/to/test/cases]
    tests.include: [media]
    tests.exclude: [media.test_case_that_is_not_working_on_my_box]
    tests.exclude_regex: [".*regex.*matching.*test.*that.*should.*not.*be.*run$"]


Test Case Parameterization
==========================

Test cases can be parameterized to be run multiple times with different values.
This is done using the :py:func:`k2.runner.decorator.foreach` decorator.

.. note::

    foreach can only be used on test cases.

Component Parameterization
--------------------------

*foreach* can act as a require, where the test case is run once for each matching component type.
This is referred as *component parameterization*. The injected component can further
be used by other requires using the `uses` argument. For more information on
components, see :ref:`Components <components>`.

.. note::

    foreach will run a test once for each matching component type! Not once for
    each available instance.

Below is an example where component parameterization is used, with can-filtering.
The test case will be run once with each matching component type.

.. code-block:: python

    from k2.runner.decorator import foreach

    @foreach(c='Component', can=['something'])
    @requires(sc='SuperComponent', uses=['c'])
    test_something(c, sc):
        pass

Data Parameterization
---------------------

*foreach* can also inject plain data specified by an iterable evaluated at load-time.
This is referred to as *data parameterization*.
The test case will be run once for every item in the iterable.

Below is an example where data parameterization is used.
The test case will be run 5 times, where d takes on the value 0 to 4.

.. code-block:: python

    from k2.runner.decorator import foreach

    @foreach(d=range(5))
    test_with_data(d):
        pass

Multiple Parameterizations
--------------------------

Multiple foreach can be used on the same test case. In that case, all combinations
of the parameterizations are used.

In the example below, the test case will be run 2x3=6 times.

.. code-block:: python

    from k2.runner.decorator import foreach

    # called with: (a,1), (a,2), (b,1), (b,2), (c,1), (c,2)
    @foreach(c=['a', 'b', 'c'])
    @foreach(d=[1, 2])
    test_with_data(c, d):
        pass

Formatting of Parameters in Reports
-----------------------------------

By default test case parameters are converted using the `str()` function in the context
of reporting. A custom formatting function can be used by using the `format` argument
in the foreach decorator. The function should take one argument (the item being formatted)
and return a string.

The @foreach decorator
----------------------

.. autoclass:: k2.runner.decorator.ForEach
   :members:
.. autofunction:: k2.runner.decorator.foreach
