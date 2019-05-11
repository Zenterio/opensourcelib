#!/usr/bin/env bash

# shellcheck disable=SC2034

USER_UID="$(id -u)"
USER_GID="$(id -g)"
USER_HOME="${HOME}"
VENV_VOLUME_NAME="${image_name}_${image_tag}"_venv
VENV_VOLUME_NAME="${VENV_VOLUME_NAME////-}"
VENV_VOLUME_NAME="${VENV_VOLUME_NAME//:/-}"
REGISTRY_URL="docker.zenterio.lan"

DOCKER_FLAGS=""
DOCKER_FLAGS+="--mount type=bind,source=/etc/passwd,target=/etc/passwd,readonly "
DOCKER_FLAGS+="--mount type=bind,source=/etc/group,target=/etc/group,readonly "
DOCKER_FLAGS+="--mount type=bind,source=$USER_HOME,target=$USER_HOME "
DOCKER_FLAGS+="--tmpfs $(pwd)/..:uid=$USER_UID,exec "
DOCKER_FLAGS+="--mount type=bind,source=$(pwd),target=$(pwd) "
DOCKER_FLAGS+="--mount type=volume,source=${VENV_VOLUME_NAME},target=$(pwd)/.venv "
DOCKER_FLAGS+="--tmpfs $(pwd)/debian:uid=$USER_UID,exec "
DOCKER_FLAGS+="-e LANG=en_US.UTF-8 -e LC_ALL=en_US.UTF-8 "
DOCKER_FLAGS+="--workdir $(pwd) -e BASH_ENV "
DOCKER_FLAGS+="--rm "
