.. _workflow-label:

********
Workflow
********

K2 provides a build system with targets for common development tasks.
This chapter provides a brief overview of what targets are available and what a typical development workflow could look like.

For more details about targets in the K2 build system:

.. code-block:: shell

    make help

For more information about the K2 development environment, see the README.md file in the K2 repository.

Static analysis and code formatting
***********************************

The K2 build system provides a suite of static analysis and code formatting tools.
These tools do things like checking PEP-8 compliance and verifying that import statements are ordered correctly.
This feature is in place to ensure that code formatting remains consistent in the K2 source tree and provides facilities for detecting some classes of coding errors.

To run the static analysis suite:

.. code-block:: shell

    make static

To automatically attempt to fix formatting errors:

.. code-block:: shell

    make format


Running tests
*************

K2 provides an extensive suite of unit- and system tests that shall be used to verify that K2 is functioning correctly following code changes.

To run the unit tests:

.. code-block:: shell

    make test

To run the system tests:

.. code-block:: shell

    make systest

Running individual tests
************************

To run an individual unit- or system test, identify the name of the test case and what package and module it belongs to.

To run an individual unit test:

.. code-block:: shell

   zk2 unittest --tests package.module:[class.]function

To run an individual system test:

.. code-block:: shell

   zk2 --config-file-pattern systest/systest_config.yaml run package.module:[class.]function


Guidelines
**********

The different targets have very different run times, where more comprehensive tests take longer to run compared to simpler ones.

To facilitate a short feedback loop when iterating on a change, a developer may opt to start with running the fast running tests.
For example, it might not be worthwile to start running any of the test suites before the static analysis pass.

An example session may include:

.. code-block:: shell

    make format
    make static
    # ... fix any errors and repeat ...

When the static tests are passing, a next step could be to start running the unit tests:

.. code-block:: shell

    make test
    # ... fix errors and repeat ...

When the unit tests are passing, a next step could be to start running the system tests:

.. code-block:: shell

    make systest
    # ... fix any errors and repeat ...

When the system tests are passing, run all tests:

.. code-block:: shell

   make check
   # ... fix any errors and repeat ...

For major changes or in cases where differences between different versions of the Python interpreter is suspected to be an issue, repeat the above steps for the applicable target environments.

To run all tests in all environments:

.. code-block:: shell

   make package
   # ... fix any errors and repeat ...
