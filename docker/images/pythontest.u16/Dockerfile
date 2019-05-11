FROM docker.zenterio.lan/zenterio/ubuntu.16

RUN apt-get update
RUN apt-get --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install curl telnet openssh-client make python3 python3-venv python3-pip moreutils build-essential socat gdebi python3.6 python3.6-venv python3.6-dev
RUN pip3 install -U setuptools nose

RUN echo "ALL    ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers
