#!/bin/bash -eux
#
# Description:
# Auto-generated script from template tag-build-step.sh (Seed scriptlet)
#  The script expects the following variables to exist:
#    JENKINS_HOME - if it is blank, push operation will not be formed, only echoed.
#    tag_name - name of the tag to be set
#    repositories - a list of pairs, name remote
#    source_tag - tag must set in repositories, otherwise script will abort
#
#  The chosen order of operations is to optimize on a transaction like behavior,
#  either the tag is applied on all repositories, or none.
#  The intention is to minimize the risk of having the tag set only in some
#  repositories, causing an inconsistent state.
#
#  The output of this script is parsed by TagBuildPingBack.groovy so be sure
#  to update that script as well if you change the output.
#
#
# Macros:
# REPOSITORIES=${REPOSITORIES}
# TAG_NAME=${TAG_NAME}
# SOURCE_TAG=${SOURCE_TAG}


do_clone_checkout()
{
    local source_tag=$1; shift
    local repositories=$*
    echo ""
    echo "Cloning repositories..."
    echo "  Source Tag: ${source_tag}"
    echo "  Repositories: ${repositories}"

    while [ $# -gt 0 ]
    do
        case $# in
            1)
                echo "      Error: Argument mismatch. Excepted at least two arguments left, found one...exiting."
                exit 1
                ;;
            *)
                local dir=${1}
                local repo=${2}
                shift 2
                echo "    -----------------------------"
                echo "    repository: $repo"
                echo "    directory:  $dir"

                if [ ! -d "${dir}" ]; then
                    git clone --recursive "$repo" "$dir"
                    cd "${WORKSPACE}/${dir}"
                    git fetch
                fi
                cd "${WORKSPACE}/${dir}"
                git checkout "${source_tag}"
                echo "                                          OK"

                cd "${WORKSPACE}"
        esac
    done
}

is_identical_duplicate_tag()
{
    local tag_name=$1
    local source_tag=$2
    if [ "$(git rev-list -1 "${source_tag}")" == "$(git rev-list -1 "${tag_name}")" ]; then
        return 0
    else
        return 1
    fi
}

do_check_duplicate_tags()
{
    local tag_name=$1; shift
    local source_tag=$1; shift
    local repositories=$*
    echo ""
    echo "Searching for duplicate tags..."
    echo "  Repositories: ${repositories}"
    echo "  Tag name:     ${tag_name}"

    while [ $# -gt 0 ]
    do
        case $# in
            1)
                echo "      Error: Argument mismatch. Excepted at least two arguments left, found one...exiting."
                exit 1
                ;;
            *)
                local dir=${1}
                local repo=${2}
                shift 2
                echo "    -----------------------------"
                echo "    repository: $repo"
                echo "    directory:  $dir"
                cd "${WORKSPACE}/${dir}"
                if [ "${tag_name}" == "$(git tag -l "${tag_name}")" ]; then
                    if is_identical_duplicate_tag "${tag_name}" "${source_tag}"; then
                        echo "Tag already exists and is identical"
                    else
                        echo "    Error: Tag duplicate ${tag_name} in $repo...exiting."
                        exit 1
                    fi
                else
                    echo "                                          OK"
                fi
                cd "${WORKSPACE}"
        esac
    done
}

do_check_valid_source_tags()
{
    local source_tag=$1; shift
    local repositories=$*
    echo ""
    echo "Checking that source tag exist in repositories..."
    echo "  Repositories: ${repositories}"
    echo "  Source Tag:   ${source_tag}"

    while [ $# -gt 0 ]
    do
        case $# in
            1)
                echo "      Error: Argument mismatch. Excepted at least two arguments left, found one...exiting."
                exit 1
                ;;
            *)
                local dir=${1}
                local repo=${2}
                shift 2
                echo "    -----------------------------"
                echo "    repository: $repo"
                echo "    directory:  $dir"
                cd "${WORKSPACE}/${dir}"
                if [ "${source_tag}" == "$(git tag -l "${source_tag}")" ]; then
                    echo "                                          OK"
                else
                    echo "    Error: Source tag ${source_tag} doesn't exist in repo ${repo}...exiting."
                    exit 1
                fi
                cd "${WORKSPACE}"
        esac
    done
}

do_tag()
{
    local tag_name=$1;shift
    local source_tag=$1;shift
    local repositories=$*
    echo ""
    echo "Tagging..."
    echo "  Repositories: ${repositories}"
    echo "  Tag name:     ${tag_name}"
    echo "  Source tag:   ${source_tag}"

    while [ $# -gt 0 ]
    do
        case $# in
            1)
                echo "      Error: Argument mismatch. Excepted at least two arguments left, found one...exiting."
                exit 1
                ;;
            *)
                local dir=${1}
                local repo=${2}
                shift 2
                echo "    -----------------------------"
                echo "    repository: $repo"
                echo "    directory:  $dir"
                cd "${WORKSPACE}/${dir}"
                echo "      Tagging repo: $repo with ${tag_name} source ${source_tag}"
                if is_identical_duplicate_tag "${tag_name}" "${source_tag}"; then
                    echo "Tag already exists and is identical"
                else
                    git tag "${tag_name}" "${source_tag}"
                fi
                echo "                                          OK"
                cd "${WORKSPACE}"
        esac
    done
}

do_push()
{
    local tag_name=$1; shift
    local repositories=$*
    echo ""
    echo "Pushing..."
    echo "  Repositories: ${repositories}"
    echo "  Tag name:     ${tag_name}"

    while [ $# -gt 0 ]
    do
        case $# in
            1)
                echo "      Error: Argument mismatch. Excepted at least two arguments left, found one...exiting."
                exit 1
                ;;
            *)
                local dir=${1}
                local repo=${2}
                shift 2
                echo "    -----------------------------"
                echo "    repository: $repo"
                echo "    directory:  $dir"
                echo "      Pushing repo: $repo, tag: ${tag_name}"
                cd "${WORKSPACE}/${dir}"
                if [ "${JENKINS_HOME}" != "" ]; then
                    git push "$(git remote)" "${tag_name}"
                else
                    echo DRY-RUN: git push "$(git remote)" "${tag_name}"
                fi

                echo "                                          OK"
                cd "${WORKSPACE}"
                ;;
        esac
    done
}

repositories=(${REPOSITORIES})
source_tag="${SOURCE_TAG}"

do_clone_checkout "${source_tag}" "${repositories[@]}"
do_check_valid_source_tags "${source_tag}" "${repositories[@]}"
# shellcheck disable=SC2154
do_check_duplicate_tags "${TAG_NAME}" "${source_tag}" "${repositories[@]}"
do_tag  "${TAG_NAME}" "${source_tag}" "${repositories[@]}"
do_push "${TAG_NAME}" "${repositories[@]}"

echo ""
echo "ALL DONE!"
echo ""
