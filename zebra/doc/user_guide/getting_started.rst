
***************
Getting Started
***************


Basic usage
===========

Help can be used to find out more about which commands exist and how they are used::

    zebra --help

Each command also has it's own help output::

    zebra <command> --help

There is also a :ref:`command-zebra_help` command to open this user guide::

    zebra help user-guide
    zebra help <command> # to open the command's page in the user guide


Building With Zebra
===================

Building with zebra make command::

    zebra make <target>

Building using the exec command::

    zebra exec make <target>

For more information about which commands exist see :ref:`list-commands`

Running other tools
===================

The Zebra images contain all necessary development tools and they can be run through the exec command::

    zebra exec gdb

It's also possible to run local scripts::

    zebra exec my_script.sh
