FROM docker.zenterio.lan/zenterio/ubuntu.18

RUN apt-get update
RUN apt-get --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install curl telnet openssh-client make python3 python3-venv python3-pip python3-dev moreutils build-essential socat gdebi
RUN pip3 install -U setuptools nose

RUN echo "ALL    ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers
