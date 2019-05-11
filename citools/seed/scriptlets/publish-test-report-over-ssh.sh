#!/usr/bin/env bash
#
# Auto-generated script from template publish-test-report-over-ssh
#
# @Summary
# Publish test report and append to summary in a specific format over SSH.
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
# SUITE_NAME=${SUITE_NAME}
# REPORT_FILE_PATTERN=${REPORT_FILE_PATTERN}
# WORKSPACE_PATH=${WORKSPACE_PATH}
# BUILD_INFO_PATH=${BUILD_INFO_PATH}
#

set -ex

# clean up
function cleanup {
    rm -r "${WORKSPACE_PATH}" || true
}

trap cleanup EXIT

# get build number from build info file
function get_image_build_number {
    grep "Build:" "${WORKSPACE_PATH}/${BUILD_INFO_PATH}" | cut -c 8-
}

# get external build number from build info file
function get_image_external_build_number {
    grep "External build number:" "${WORKSPACE_PATH}/${BUILD_INFO_PATH}" | cut -c 24-
}

# $1 = test result XML file
function get_test_result {
    local xml_file="$1"
    local testdata=($(grep -m1 testsuites "${xml_file}" | sed -E "s/.*disabled=\"([0-9]+)\" errors=\"([0-9]+)\" failures=\"([0-9]+)\" tests=\"([0-9]+)\" time.*/\1\n\2\n\3\n\4/"))
    local disabled=${testdata[0]}
    local errors=${testdata[1]}
    local failures=${testdata[2]}
    local total=${testdata[3]}
    local passed=$((total - disabled - errors - failures))
    local failed=$((errors + failures))
    local test_result=${passed}/${failed}/${disabled}/${total}
    echo "${test_result}"
}

# $1 = suite name
# $2 = file count
# $3 = loop count
function get_loop_suite_name {
    local suite_name="$1"
    local file_count=$2
    local loop_count=$3
    if (( file_count > 1 ));
    then
        echo "${suite_name} ${loop_count}"
    else
        echo "${suite_name}"
    fi
}

# $1 = loop suite name
function get_output_file_name {
    local output_file="${1,,}"
    output_file="${output_file// /_}"
    output_file="${output_file}_report.xml"
    echo "${output_file}"
}

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

# $1 - image build number
# $2 - image external build number
# $3 - publishing directory prefix/initial path
do_publishing() {
    local image_build_number=$1
    local image_external_build_number=$2
    local publish_dir_prefix=$3
    local publish_dir_suffix
    # shellcheck disable=SC2010
    publish_dir_suffix=$(ls "${publish_dir_prefix}" | grep -m1 "${image_build_number}-ext-${image_external_build_number}" )
    local publish_dir="${publish_dir_prefix}${publish_dir_suffix}"
    local report_files
    report_files="$(find "${WORKSPACE_PATH}" -type f ! -name "$(basename "${BUILD_INFO_PATH}")")"
    local file_count; file_count=$(echo "${report_files}" | wc -l)
    local loop_count=1
    local test_result
    local loop_suite_name
    local output_file

    if [ -z "${report_files}" ]; then
        echo "The configured report-file-pattern '${REPORT_FILE_PATTERN}' did not match any files."
        echo "This is usually a result of misconfiguration. Please contact engineering services."
        echo "This error will cause the job to be marked as UNSTABLE, even if all tests passed."
        exit 1
    fi

    if [ ! -d "${publish_dir}" ]; then
        echo "Publishing directory '${publish_dir}' could not be located."
        echo "Make sure the build has been published - test report will not be published!"
        echo "This error will cause the job to be marked as UNSTABLE, even if all tests passed."
        exit 1
    fi

    loop_suite_name="$(get_loop_suite_name "${SUITE_NAME}" "${file_count}" "${loop_count}")"
    output_file="$(get_output_file_name "${loop_suite_name}")"
    if  grep "${loop_suite_name}" "${publish_dir}/${TEST_RESULT_FILE}" | grep -q "${output_file}"; then
        echo "Report already published - test report will not be published again"
        exit 0
    fi

    while read -r report_file; do
        local test_result; test_result="$(get_test_result "${report_file}")"
        loop_suite_name="$(get_loop_suite_name "${SUITE_NAME}" "${file_count}" "${loop_count}")"
        output_file="$(get_output_file_name "${loop_suite_name}")"

        printf "${TEST_REPORT_FORMAT}" "${loop_suite_name}" "${test_result}" "${output_file}" >> "${publish_dir}/${TEST_RESULT_FILE}"
        mkdir -p "${publish_dir}/$(dirname "${output_file}")"
        cp "${report_file}" "${publish_dir}/${output_file}"
        loop_count=$((loop_count + 1))
    done <<< "${report_files}"
}

# Everything is relative to workspace, do not change working directory.
cd workspace

image_build_number=$(get_image_build_number)
image_external_build_number=$(get_image_external_build_number)
publish_dir_prefix="${ROOT_DIR}/${PRODUCT_ALT_NAME}/${PUBLISH_TYPE}/"

if [ -z "${image_build_number}" ]; then
    echo "Image build number could not be established - test report will not be published!"
    echo "This should not happen! Please contact engineering services for further investigation."
    echo "This error will cause the job to be marked as UNSTABLE, even if all tests passed."
    exit 1
fi

if [ -z "${image_external_build_number}" ]; then
    echo "Image external build number could not be established - test report will not be published!"
    echo "This happens if you are testing a compilation build that was built without external build number."
    exit 0
fi

if [ ! -d "${publish_dir_prefix}" ]; then
    echo "Image publishing directory '${publish_dir_prefix}' could not be located."
    echo "The test report will not be published!"
    echo "Make sure that the build has been successfully published before trying to publish test results."
    echo "This error will cause the job to be marked as UNSTABLE, even if all tests passed."
    exit 1
fi

mount_if_mount_point_in_path "${publish_dir_prefix}"
do_publishing "${image_build_number}" "${image_external_build_number}" "${publish_dir_prefix}"
