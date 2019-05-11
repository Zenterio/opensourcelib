#!/usr/bin/env bash

set -exu

cd /root/docs_fetcher

python3 -m docs_fetcher &
httpd-foreground
