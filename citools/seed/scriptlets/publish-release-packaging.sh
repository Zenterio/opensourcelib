#!/bin/bash
#
# Auto-generated script from template publish-release-packaging.sh
#
# @Summary
# Publish the content of a specified directory to a release directory
#
# Warning: Publish over ssh-commands do not support regular bash variable expansions, so advanced features like
# ${var-} cannot be used
#
# Jenkins parameters:
# annotation            ${annotation}
# target_build_number   ${target_build_number}
#
# Macros:
# PROJECT               ${PROJECT}
# JOB                   ${JOB}
# ORIGIN                ${ORIGIN}
# PUBLISH_ROOT          ${PUBLISH_ROOT}
# CONTENT_DIR           ${CONTENT_DIR}
#
set -ex

declare annotation
declare target_build_number

CURRENT_DATE=$(date +%Y-%m-%d)

TARGET_EXTERNAL_BUILD_NUMBER=${target_build_number}

PUBLISH_PATH="${PROJECT}/${ORIGIN}/${CURRENT_DATE}-build-${target_build_number}-ext-${TARGET_EXTERNAL_BUILD_NUMBER}-${annotation}"
RELEASE_PATH="${PUBLISH_ROOT}/${PUBLISH_PATH}"

mkdir -p "${RELEASE_PATH}"
rsync -r ${CONTENT_DIR}/* "${RELEASE_PATH}"
rm -rf "${CONTENT_DIR}"
