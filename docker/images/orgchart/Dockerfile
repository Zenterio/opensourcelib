FROM docker.zenterio.lan/httpd:latest

RUN \
apt-get update && \
apt-get install -y --no-install-recommends python3 python3-pip && \
rm -r /var/lib/apt/lists/*

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

COPY org_chart_generator /root/org_chart_generator
RUN pip3 install setuptools
RUN pip3 install requests==2.21.0 click==7.0

RUN rm /usr/local/apache2/htdocs/index.html
COPY run.sh /root/run.sh

HEALTHCHECK CMD netstat -an | grep 80; if [ 0 != $? ]; then exit 1; fi;
HEALTHCHECK CMD ls /usr/local/apache2/htdocs/*

WORKDIR /root
CMD ["/bin/bash", "run.sh"]
