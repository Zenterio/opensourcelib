#!/bin/bash -eu
#
# Description:
#   Test script that tests the scriptlet tag-build-step.sh
#   It makes several runs with different checks
#   The output is not parsed but is intended to be looked at by a human
#   because it involves estetics such as printouts.
#

#set to echo if "DRY-RUN"
EXEC=

# push is not done because JENKINS_HOME is not set.
export JENKINS_HOME=
SEED_ROOT=$(cd `dirname "$0"`; cd ../../..; pwd)
WORKSPACE=${SEED_ROOT}/build/test_tag-build-step-sh
SCRIPT_SUT=${SEED_ROOT}/scriptlets/tag-build-step.sh
$EXEC mkdir -p "${WORKSPACE}"
$EXEC pushd "${WORKSPACE}"

# Variables used by the script
export tag_name="DROP_4_SPRINT_1"
export repositories="product-stub git@git.zenterio.lan:product-stub"
export source_tag="DROP_4"

echo "WORKSPACE=$WORKSPACE"

# Clean up in case script have been run and failed before.
rm -rf ${WORKSPACE}/product-stub
rm -rf ${WORKSPACE}/verification

echo ""
echo "*** TEST: INVALID SOURCE TAG ***"
export source_tag="TAG_DOES_NOT_EXIST"
export repositories="product-stub git@git.zenterio.lan:product-stub"
$EXEC ${SCRIPT_SUT} || true

echo ""
echo "*** TEST: VALID SOURCE TAG - ONE REPO ***"
export tag_name="DROP_4_SPRINT_1"
export source_tag="DROP_4"
export repositories="product-stub git@git.zenterio.lan:product-stub"
$EXEC ${SCRIPT_SUT}

echo ""
echo "*** TEST: APPLY TAG THAT ALREADY EXISTS - ONE REPO ***"
export tag_name="DROP_4_SPRINT_1"
export source_tag="DROP_4"
export repositories="product-stub git@git.zenterio.lan:product-stub"
$EXEC ${SCRIPT_SUT} || true

echo ""
echo "*** TEST: INVALID SOURCE TAG FOR SECOND REPO - TWO REPOS ***"
export tag_name="DROP_4_SPRINT_2"
export source_tag="DROP_4"
export repositories="product-stub git@git.zenterio.lan:product-stub verification git@git.zenterio.lan:verification"
$EXEC ${SCRIPT_SUT} || true

echo ""
echo "*** TEST: VALID SOURCE TAG - TWO REPOS ***"
export tag_name="DROP_4_SPRINT_2"
export source_tag="DROP_4"
export repositories="product-stub git@git.zenterio.lan:product-stub verification git@git.zenterio.lan:verification"
$EXEC cd verification
$EXEC git tag ${source_tag}
$EXEC cd ..
$EXEC ${SCRIPT_SUT}

# Clean up
$EXEC popd
$EXEC rm -rf "${WORKSPACE}"

echo ""
echo "*** TEST DONE ***"
