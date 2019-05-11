
*****************
Build Environment
*****************

K2 uses make for its build system. Targets are provided for tasks such as running tests and packaging K2 for distribution.


For details on how to set up a local development environment, please see the README.md file in the K2 repository root directory.


For details on what make targets are available, please see:

  make help


Environments
============

K2 is intended to support multiple different Python interpreters and environments.
This presents a problem in that K2 may behave differently depending on what Python interpreter or tools are available.


To facilitate testing and packaging K2 for different environments, the K2 build system offers the following flavors of execution environments:


  * local - Use the local systems Python interpreter and tools
  * 14 - Use a Docker container with the necessary Ubuntu 14.04 runtime
  * 16 - Use a Docker container with the necessary Ubuntu 16.04 runtime
  * all - Use each of the above environments


Execution
=========

Each build environment is expected to provide a build and a run script.


The build script prepares the environment for use and takes a single argument, the name of the environment.


The run script executes a command in the target environment.
It assumes that the environment has been built and takes one or more arguments, where the first argument is the name of the environment and the rest of the arguments is the command to run.


The run script is expected to behave as if running `bash -c "command"` in the target environment.


Make Specific Details
*********************

The `SHELL` and `.SHELLFLAGS` variables are used to specify what build or run script to use for a specific target.
The `SHELL` variable will contain the script to use and the `.SHELLFLAGS` will contain the name of the environment.


K2 makes use of Python virtual environments, which need to be activated before use.
To ensure that the virtual environment is always activated if available, the build system ensures that the activation script is placed under `.venv/bin/activate` and sets the `BASH_ENV` environment variable to this location to get bash to automatically source it when launched.


Local Environment
=================

Files:

  * ./maketools/local/build.sh
  * ./maketools/local/run.sh


Docker Environment
==================

Files:

  * ./docker/Dockerfile.<environment name>
  * ./maketools/docker/build.sh
  * ./maketools/docker/run.sh
