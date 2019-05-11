#!/bin/bash -eux
#
# Description:
# Auto-generated script from template generate-changelog.sh (Seed scriptlet)
#  The script expects the following variables to exist:
#    JIRA_USERNAME - Provided by the jenkins-jira-user credential
#    JIRA_PASSWORD  - Provided by the jenkins-jira-user credential
#    tag_name - name of the tag used for the current release
#    previous_tag_name - name of the tag used for the previous release
#
# Macros:
# REPOSITORIES=${REPOSITORIES}
# CURRENT_RELEASE=${CURRENT_RELEASE}
# PREVIOUS_RELEASE=${PREVIOUS_RELEASE}

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

do_generate_changelog()
{
    local previous_tag_name=$1; shift
    local tag_name=$1; shift
    local repo_flags=()

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
                repo_flags+=("--repo" "${WORKSPACE}/${dir}")
        esac
    done
    echo ""
    echo "Generating changelog from previous to current tag"
    echo "  Previous: ${previous_tag_name}"
    echo "  Current:   ${tag_name}"
    mkdir -p "${WORKSPACE}/result"
    zchangelog -u "${JIRA_USERNAME}" -p "${JIRA_PASSWORD}" "${repo_flags[@]}" changelog "${previous_tag_name}" "${tag_name}" --txt "${WORKSPACE}/result/changelog.txt" --xml "${WORKSPACE}/result/changelog.xml" --json "${WORKSPACE}/result/changelog.json"
}

repositories=(${REPOSITORIES})
previous_release=${PREVIOUS_RELEASE}

if [ -z "${previous_release}" ]; then 
    echo "No previous release set, not generating changelog"
    exit 0; 
fi
declare git_tag_name
current_release=${CURRENT_RELEASE}

do_check_valid_source_tags "${previous_release}" "${repositories[@]}"
do_generate_changelog "${previous_release}" "${current_release}" "${repositories[@]}"

echo ""
echo "ALL DONE!"
echo ""
