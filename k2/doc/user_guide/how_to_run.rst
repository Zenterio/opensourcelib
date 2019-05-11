.. _how_to_run-label:

**********
How to run
**********

K2 can either be run by installing the *zenterio-zk2* debian package from the `Zenterio PPA <https://wiki.zenterio.lan/index.php/Zenterio_PPA>`_
or by checking out the *k2* repository (git\@git.zenterio.lan:k2).

The test cases and Zenterio specific addons are included in the k2-verification repository 

Install from Debian package
===========================

Add the `Zenterio PPA <https://wiki.zenterio.lan/index.php/Zenterio_PPA>`_ and install the package.

.. code-block:: shell

    sudo apt update
    sudo apt install zenterio-zk2

.. _run_from_source-label:

Run from Source
===============

Running from source is done using a Python virtual environment.
On Ubuntu systens this requires the installation of the *python3-venv* package.
Sourcing the *activate* script installs K2 in the current shell.

.. code-block:: shell

    sudo apt update
    sudo apt install python3-venv
    git clone git@git.zenterio.lan:k2
    cd k2
    source ./activate

Running K2
==========

Test cases for Zenterio STBs are placed in the *k2-verification* repository.
K2 has a huge number of :ref:`configuration options <list-config_option_ids>` but for the simplest runs it is enough
to specify the :ref:`sut ip <option-suts.\<ids\>.ip>`, and if correct software isn't already loaded the :ref:`path/url of the kfs <option-suts.\<ids\>.flash.kfs>`.

All sut specific options to K2 are connected to a :ref:`sut id <option-suts.ids>` because K2 supports multiple suts that could have different configuration.
The \@-sign in the command line arguments indicates that an option is specified for an id.

.. code-block:: shell

    zk2 run \
        --suts-ids mystb \
        --suts-mystb@ip <ip number to the stb> \
        --suts-mystb@flash-kfs <path/url to the KFS> \
        <path to directory or file with tests>

For more information about configuration see :ref:`configuration`.
