
To get Systemd init and Docker in Docker to work, run using:

  $ docker run --privileged --mount type=bind,source=/sys/fs/cgroup,target=/sys/fs/cgroup,readonly --tmpfs /run <ID>
