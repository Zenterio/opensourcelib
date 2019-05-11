#!/bin/bash -eux
#
# Description:
# Auto-generated script from template save-release-description.sh (Seed scriptlet)
#  The script expects the following variables to exist:
#   description: description of the release
#   git_tag_name: name of the release tag
#   annotation: Text to annotate the tag with
#
#  Writes release description and tag to a description-file in the results folder
#
# Macros:
# ARTIFACTS_PATH=${ARTIFACTS_PATH}
#
# Disables the check "var is referenced but not assigned" for the entire file because it has several external variables with lowercase names
# shellcheck disable=SC2154

DESCRIPTION_FILE="${ARTIFACTS_PATH}/description.txt"

{
echo "${annotation}"
echo "${annotation//?/-}"
echo "git tag: ${git_tag_name}"
echo "description:"
echo "${description}"
} > "${DESCRIPTION_FILE}"