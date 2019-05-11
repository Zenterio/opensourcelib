FROM centos/systemd

RUN \
  systemctl enable systemd-user-sessions.service && \
  ln -s /usr/lib/systemd/system/systemd-user-sessions.service /etc/systemd/system/default.target.wants/systemd-user-sessions.service

VOLUME /var/lib/docker

CMD ["/usr/sbin/init"]
