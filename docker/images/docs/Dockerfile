FROM docker.zenterio.lan/httpd:latest

RUN \
apt-get update && \
apt-get install -y --no-install-recommends python3 python3-pip && \
rm -r /var/lib/apt/lists/*

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

COPY docs_fetcher /root/docs_fetcher
RUN pip3 install setuptools
RUN pip3 install artifactory==0.1.17 click==6.7

COPY run.sh /root/run.sh

HEALTHCHECK CMD netstat -an | grep 80; if [ 0 != $? ]; then exit 1; fi;
HEALTHCHECK CMD ls /usr/local/apache2/htdocs/*

WORKDIR /root
CMD ["/bin/bash", "run.sh"]
