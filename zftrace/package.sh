#!/bin/bash
zebra "$@" --network bridge --env-variable BUILD_NUMBER --image-override zenterio/zftrace.u14 --root-dir .. exec ./make-deb
