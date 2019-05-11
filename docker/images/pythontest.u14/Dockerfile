FROM docker.zenterio.lan/zenterio/ubuntu.14

RUN apt-get update
RUN apt-get --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install curl telnet openssh-client make moreutils python3 python3.4-venv build-essential socat gdebi python3.6 python3.6-venv python3.6-dev

# The python3.6-venv and python3-pip packages are in conflict, where python3.6-venv is said to break python3-pip.
# This does not seem to be the case. Install it anyway...
RUN apt-get download python3-pip && dpkg -i --force-all python3-pip*.deb && rm python3-pip*.deb
# ... and then defeat APTs breakage check.
RUN sed -i -e '/Breaks: python3-pip (<< 1.5.6-4)/d' -e '/Breaks: python3-pip.4 (<< 1.5.6-4)/d' /var/lib/dpkg/status
RUN apt -f --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" install

RUN pip3 install -U setuptools nose

RUN echo "ALL    ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers