
******
Docker
******

K2 targets a collection of different Linux distributions and Python versions.

Packages are built and tested in the following environments:

* Ubuntu 14.04 with Python 3.4
* Ubuntu 16.04 with Python 3.5
* Ubuntu 18.04 with Python 3.6

Each target environment is made available as a Docker container that are used by the K2 build system.

Usage
*****

Most K2 build system targets support running in either the local environment or in a docker container.
To be able to run targets that require a Docker container, Docker must be installed on the local system and the current used must be a member of the "docker" group.

For example, the unit tests can be run in different environments:

.. code-block:: shell

    # Run the unit tests in the local environment
    make test

    # Run the unit tests in a Ubuntu 16.04 Docker container
    make test_16

For more information about what targets are available:

.. code-block:: shell

    make help

