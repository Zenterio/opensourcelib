ZFTRACE
=======

Zftrace is based on the open source project "Revisor", which in turn is based
on strace.

Development
-----------

To start the build-environment:

    zebra --image-override zenterio/zftrace.u14 shell

To configure the make system, when in zebra, run:

    ./setup-dev

To build the product, when in zebra, run:

    make

To run all tests, when in zebra, run:

    make check

To create debian package (will require ./configure again), when in zebra, run:

    ./make-deb

To create debian package from outside zebra, run:

    ./package.sh

Before push

    step version in VERSION and update CHANGELOG
    Use the token @ZFTRACE_VERSION@ for the current version.
    Change previous version to use explicit version instead of @ZFTRACE_VERSION@.
