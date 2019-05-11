
.. _caching:

*******
Caching
*******

Zebra normalizes paths and controls the environment in a way that makes it possible to share caches between computers.
Caching is supported by downloading and uploading cache files with the :ref:`command-zebra_cache` command.


Ccache
======

Zebra allows the use of the normal local ccache as long as it is placed in the home directory
or if the ccache directory is mounted into the Docker container (See :ref:`option-mount`).
