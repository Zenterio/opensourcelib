FROM docker.zenterio.lan/zenterio/ubuntu.16

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV IPTABLES_COMMAND=echo
ENV TC_COMMAND=echo
ENV HUB_CTRL_COMMAND=echo
ENV SERVICE_COMMAND=echo
ENV HOSTS_FILE=/dev/null

EXPOSE 80

RUN \
apt-get update && \
apt-get --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install unzip net-tools

RUN mkdir -p /tmp/znail
WORKDIR /tmp/znail

RUN \
curl -O "https://ci-tools.zenterio.lan/job/Zenterio_Znail_release/lastSuccessfulBuild/artifact/zenterio-znail/dist/xenial/*zip*/xenial.zip" && \
unzip xenial.zip && \
apt install --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" "$(ls ./xenial/zenterio-znail_*.deb)"

HEALTHCHECK CMD netstat -an | grep 80; if [ 0 != $? ]; then exit 1; fi;

ENTRYPOINT ["/usr/bin/znail"]