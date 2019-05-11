#!/usr/bin/env bash

set -exu

cd /root/org_chart_generator

cp org_chart_generator/data/* /usr/local/apache2/htdocs

python3 -m org_chart_generator --update-interval 600 --output /usr/local/apache2/htdocs/index.html http://URL-TO-DATA-SRC/orgcharts.csv &
httpd-foreground
