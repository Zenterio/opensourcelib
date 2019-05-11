#!/usr/bin/env bash
#
# Auto-generated script from template publish-build-over-ssh.sh
#
# @Summary
# Publish artifacts in a specific format over SSH.
#
# Warning: Publish over ssh-commands do not support regular bash variable expansions, so advanced features like
# ${var-} cannot be used
#
# Macros:
# ROOT_DIR=${ROOT_DIR}
# PRODUCT_ALT_NAME=${PRODUCT_ALT_NAME}
# PUBLISH_TYPE=${PUBLISH_TYPE}
# TEST_REPORT_FORMAT=${TEST_REPORT_FORMAT}
# TEST_RESULT_FILE=${TEST_RESULT_FILE}
# NUMBER_OF_BUILDS_TO_KEEP=${NUMBER_OF_BUILDS_TO_KEEP}
# WORKSPACE_PATH=${WORKSPACE_PATH}
# PREPARE_FOR_TEST_REPORT=${PREPARE_FOR_TEST_REPORT}
#
set -ex

# clean up
function cleanup {
    rm -r "${WORKSPACE_PATH}" || true
}

trap cleanup EXIT

# $1 - dirpath
mount_if_mount_point_in_path() {
    local dirpath="$1"
    local mount_points; mount_points=$(findmnt --fstab --output=target | tail -n +2 | grep -ve '^/$' | sort)
    local mp

    for mp in ${mount_points}; do
        if [[ "${dirpath}" == "${mp}"* ]]; then
            if ! ls "${mp}"/* &> /dev/null; then
                mount "${mp}" || true
            fi
        fi
    done
}

# Everything is relative to workspace, do not change working directory.
cd workspace

# We only publish official builds and all official builds have external build number.
# shellcheck disable=SC2154
if [ -z "${external_build_number}" ]; then
    echo "The external build number was not set for this job."
    echo "This usually indicate that the job was started manually - the build will not be published!"
    exit 0
fi

mount_if_mount_point_in_path "${ROOT_DIR}"
PUBLISH_DIR="${ROOT_DIR}/${PRODUCT_ALT_NAME}/${PUBLISH_TYPE}/$(date +%Y-%m-%d)-build-${BUILD_NUMBER}-ext-${external_build_number}/"

if [ -d "${PUBLISH_DIR}" ]; then
    echo "The publishing destination directory already exists. This should not happen!"
    echo "Please contact engineering services for further investigation."
    exit 1
fi

mkdir -p "${PUBLISH_DIR}"
mv "${WORKSPACE_PATH}"/* "${PUBLISH_DIR}"
if ${PREPARE_FOR_TEST_REPORT}; then
    printf "${TEST_REPORT_FORMAT}" "Test Suite" "P/F/S/T" "Detailed report" > "${PUBLISH_DIR}"/${TEST_RESULT_FILE}
    printf "${TEST_REPORT_FORMAT}" "" "" ""| tr ' ' - >> "${PUBLISH_DIR}"/${TEST_RESULT_FILE}
fi

(cd "$(dirname "${PUBLISH_DIR}")";
 while [ "$(find . -mindepth 1 -maxdepth 1 -type d | wc -l)" -gt ${NUMBER_OF_BUILDS_TO_KEEP} ] ;
 do find . -mindepth 1 -maxdepth 1 -type d -print | sort -n | head -n 1 | xargs rm -r;
 done)
