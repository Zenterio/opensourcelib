Test run
********

The test run is handled as a cooperation between the testrunner, testscheduler and testfinder extensions.

testrunner:
   Responsible for running a test case and for sending out events related to the ongoing test run.

testscheduler:
    Responsible for which test cases to run and provides an API for looking at and modifying the run queue.

testfinder:
    Responsible for finding and loading the test cases.


A test run
==========

.. uml::

    participant runcommand
    participant testrunner
    participant testscheduler
    participant testfinder
    collections listeners

    activate runcommand
    runcommand -> runcommand: preparation
    runcommand -> testrunner: TEST_RUN
    activate testrunner

    testrunner -> listeners: TEST_RUN_STARTED
    testrunner -> testscheduler: SCHEDULE_NEXT_TEST
    activate testscheduler
    testscheduler -> testfinder: FIND_TEST_CASES
    activate testfinder
    testfinder -> testscheduler: List of all found test cases
    deactivate testfinder
    testscheduler -> testscheduler: Filter list of test cases using config
    testscheduler -> testrunner: Test case

    loop until no more test cases
        testrunner -> listeners: TEST_CASE_STARTED
        testrunner -> testrunner: Run test case
        testrunner -> listeners: TEST_CASE_FINISHED
        testrunner -> testscheduler: SCHEDULE_NEXT_TEST
        testscheduler -> testrunner: Test case or None
    end
    deactivate testscheduler
    testrunner -> listeners: TEST_RUN_FINISHED
    testrunner -> runcommand:
    deactivate testrunner
    runcommand -> runcommand: cleanup
