FROM docker.zenterio.lan/zenterio/ubuntu.18

RUN \
apt-get update && \
apt-get install --yes -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" openssh-server openjdk-11-jre-headless
RUN mkdir /var/run/sshd

COPY ssh /root/.ssh

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
