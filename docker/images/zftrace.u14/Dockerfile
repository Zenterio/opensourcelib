FROM docker.zenterio.lan/zenterio/ubuntu.14

LABEL description="An Ubuntu 14.04 image that can be used to build zftrace."

RUN \
apt-get update && \
apt-get --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" --no-install-suggests install \
build-essential \
libc6-dev \
debhelper \
libmhash-dev \
libglib2.0-dev \
autoconf \
libaio-dev
