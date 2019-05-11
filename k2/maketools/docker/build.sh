#!/usr/bin/env bash
#
# $1 the name to use for the image locally
# $2 the tag to use for the image locally
# $3 docker image
# $4 make marker file
image_name=$1
image_tag=$2
image=$3
marker_file=$4

set -ue

source ./maketools/docker/common.sh

docker volume rm -f "${VENV_VOLUME_NAME}" || true
docker volume create "${VENV_VOLUME_NAME}"
# shellcheck disable=SC2086
docker run --rm ${DOCKER_FLAGS} ${REGISTRY_URL}/zenterio/ubuntu.16 chown "${USER_UID}:${USER_GID}" "$(pwd)/.venv"

docker pull "${REGISTRY_URL}/${image}"
touch "${marker_file}"
