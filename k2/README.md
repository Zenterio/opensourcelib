
# Running K2

    zk2 --help

# Developing K2
After setting up the python environment and generating the documentation,
additional development guide-lines can be found in the generated dev-guide
documentation.

## Setup python environment
To setup the python development environment, run:

    source ./activate

## Generating Documentation
To generate the documentation, install:

    apt-get install texlive-full

and run:

    make doc

The generated documentation will appear in doc/build

## Setup dev environment

Developing K2 requires at least Python 3.6.

The following tools are necessary

    sudo apt-get install docker-ce
    sudo apt-get install socat

Extra tools on Ubuntu (Debian)

    sudo apt-get install python3.6-venv

## Debugging deb package builds in docker

K2 uses docker to build deb packages for all supported systems.
To be able to trouble-shoot failing builds or tests of the deb packages
it is possible to start a docker container and manually perform the tests in it.
This can be done by running the script.

    maketools/docker/debug.sh
