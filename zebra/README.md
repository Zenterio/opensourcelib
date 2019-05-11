
# Running Zebra

    zebra --help

## Setup python environment
To setup the python development environment, run:

    source activate

## Generating Documentation
To generate the documentation, install:

    apt-get install texlive-full

and run:

    make doc

The generated documentation will appear in doc/build

## Setup dev environment

Developing Zebra requires at least Python 3.4.

The following tools are necessary

    sudo apt-get install docker-ce

Extra tools on Ubuntu (Debian)

    sudo apt-get install python3-venv
