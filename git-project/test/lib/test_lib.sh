#
# Dependencies to variables:
#
# TEMPLATE_PATH
# SWUPDATE_PATH
# ORIGIN_PROJECT_PATH
#
# FULL_PROJECT_PATH
# COMPONENT_PATH
# COMPONENT2_PATH
# SPACE_COMPONENT_PATH
# SUBCOMPONENT_PATH
# THIRDPARTY_COMPONENT_PATH
#
# REPO_EXT
# SHARNESS_TRASH_DIRECTORY
# SHARNESS_BUILD_DIRECTORY
# INSTALL_DIR
# SUT_DIR

set_config() {
    git config project.template "${TEMPLATE_PATH}"
    git config project.update-repo "${SWUPDATE_PATH}"
    git config user.email "test@test.com"
    git config user.name "test user"
    if test_have_prereq SYSTEM_TEST; then
        git config project.install.destdir "$(unset GIT_CONFIG; git config project.install.destdir)"
        git config project.install.prefix "$(unset GIT_CONFIG; git config project.install.prefix)"
        git config project.install.htmlprefix "$(unset GIT_CONFIG; git config project.install.htmlprefix)"
        git config project.install.git-doc "$(unset GIT_CONFIG; git config project.install.git-doc)"
        git config project.install.completionprefix "$(unset GIT_CONFIG; git config project.install.completionprefix)"
        git config project.install.bin "$(unset GIT_CONFIG; git config project.install.bin)"
        git config project.install.man "$(unset GIT_CONFIG; git config project.install.man)"
        git config project.install.html "$(unset GIT_CONFIG; git config project.install.html)"
        git config project.install.completion "$(unset GIT_CONFIG; git config project.install.completion)"
        git config project.install.method "$(unset GIT_CONFIG; git config project.install.method)"
    fi
}

# $1 path to top repo
set_config_recursive() {
    local top; top="$1"
    pushd "${top}" > /dev/null
    (unset GIT_CONFIG && set_config)
    while read -r path; do
        (cd "${path}" && unset GIT_CONFIG && set_config)
    done <<< "$(git project --all-submodules)"
    popd > /dev/null
}

init_repo_variable() {
    local name=$1
    local varname=$(echo $1 | tr '[a-z ]' '[A-Z_]')
    printf -v "${varname}_NAME" "${name}${REPO_EXT}"
    printf -v "${varname}_PATH" "${SHARNESS_TRASH_DIRECTORY}/${name}${REPO_EXT}"
}


# $1 repo
# $2 path
# $3 branch
# Branch is optional (this allows cloning empty repositories without error)
# Path should typically be "$(mktemp -d)" but because we want to handle
# errors this function can't return both error code and string value.
clone_temporary_repository() {
    local repo=$1
    local repo_path=$2
    local branch=$3
    local result
    if [ ! -z "$branch" ]
    then
        git clone -q --recurse-submodules "${repo}" -b "${branch}" "${repo_path}" &>/dev/null
        result=$?
    else
        git clone -q --recurse-submodules "${repo}" "${repo_path}" &>/dev/null
        result=$?
    fi
    return ${result}
}

# $1 - repo-directory
# creates a simulated remote (bare) repository with repo.info file
create_remote_repo() {
    local repo_dir="$1"
    create_empty_remote_repo "${repo_dir}"
    add_to_remote_repo "${repo_dir}" "Added repo.info" "echo ${repo_dir} > repo.info; echo '*.ignore' >.gitignore"
}

# $1 - repo directory
# creates a simulated empty remote (bare) repository
create_empty_remote_repo() {
    git init -q --bare "$1"
}

# $1 - repo directory
# creates a local repository
create_repo() {
    git init -q "$1" &&
    test_when_finished "rm -rf ${SHARNESS_TRASH_DIRECTORY}/$1" &&
    set_config_recursive "$1" &&
    unset GIT_CONFIG &&
    cd "$1" &&
    add_to_repo . "initial commit" "touch initial_file" &&
    cd ..
}

# $1 - repo
# $2 - branch
# $3 - commit message
# $4 - commands to be run before commit
# adds to a remote repository by committing all changes caused by commands.
# requires that the branch exists
add_to_remote_repo_branch() {
    local repo="$1"
    shift
    local branch="$1"
    shift
    local msg="$1"
    shift
    commands="$@"
    local dir=$(basename "${repo}" ${REPO_EXT})
    (git clone -q --recurse-submodules -b "$branch" "${repo}" "${dir}" &&
     add_to_repo "${dir}" "${msg}" "${commands}" &&
     pushd "${dir}" >/dev/null &&
     git push -q origin "${branch}":"${branch}" &&
     popd >/dev/null;
     result=$?;
     rm -rf "${dir}"; return $result) &>/dev/null
}

# $1 - repo
# $2 - commit message
# $3 - commands to be run before commit
# adds to a remote repository by committing all changes caused by commands.
# Blindly assumes that HEAD is master
add_to_remote_repo() {
    local repo="$1"
    shift
    local msg="$1"
    shift
    commands="$@"
    local dir="$(mktemp -d)"
    (clone_temporary_repository "${repo}" "${dir}" &&
     add_to_repo "${dir}" "${msg}" "${commands}" &&
     pushd "${dir}" >/dev/null &&
     git push -q origin master:master &&
     popd >/dev/null;
     result=$?;
     rm -rf "${dir}"; return $result) &>/dev/null
}

# $1 - repo
# $2 - source branch
# $3 - destination branch
create_remote_branch() {
    local repo="$1"
    local source="$2"
    local branch="$3"
    local dir="$(mktemp -d)"
    local result
    clone_temporary_repository "${repo}" "${dir}" "${source}"
    result=$?
    if [ ${result} -ne 0 ]
    then
        echo "Create remote branch aborted"
        rm -rf "${dir}"
        return ${result}
    fi
    pushd "$dir" >/dev/null
    git push -q origin "$source":"$branch"
    result=$?
    popd >/dev/null
    rm -rf "${dir}"
    return $result
}

# $1 - repo
# $2 - commit message
# $3 - commands to be run before add and commit
# adds to a local repository by committing all changes caused by commands.
add_to_repo() {
    local repo="$1"
    shift
    local msg="$1"
    shift
    commands="$@"
    (pushd "${repo}" >/dev/null &&
        eval "${commands}" &&
        git add --all . &&
        (unset GIT_CONFIG;
            git config user.name "test user" &&
            git config user.email "test@test.com" &&
            git commit -q -m "${msg}") &&
        popd  >/dev/null)
}

# $1 - parent repo
# $2 - module repo
# $3 - module path
add_submodule_to_remote_repo() {
    local parent_repo="$1"; shift
    local module_repo="$1"; shift
    local module_path="$1"; shift
    local dir=$(basename "${parent_repo}" ${REPO_EXT})
    (git clone -q "${parent_repo}" "${dir}" &&
    add_submodule_to_repo "${dir}" "${module_repo}" "${module_path}" &&
    pushd "${dir}" >/dev/null &&
    git push -q origin master:master &&
    popd >/dev/null;
    result=$?;
    rm -rf "${dir}"; return $result)
}

# $1 - parent repo
# $2 - module repo
# $3 - module path
add_submodule_to_repo() {
    local parent_repo="$1"; shift
    local module_repo="$1"; shift
    local module_path="$1"; shift
    local msg="Added submodule (path=${module_path}, repo=${module_repo})"
    local commands='
        git submodule -q add -b master "${module_repo}" "${module_path}" &&
        git add "${module_path}"
    '
    add_to_repo "${parent_repo}" "${msg}" "${commands}"
}


# $@ make arguments
run_make() {
    cd "${SHARNESS_BUILD_DIRECTORY}" &&
    make --no-print-directory "$@"
}

# creates a simulated remote repo called template
create_template() {
    create_remote_repo "${TEMPLATE_PATH}" &&
    add_to_remote_repo "${TEMPLATE_PATH}" 'added src directory' '
        mkdir src &&
        echo "src" > src/src.info
        '
}

# create a simulated remote swupdate repo based on latest commit in local repo
create_update_repo() {
    create_remote_repo "${SWUPDATE_PATH}" &&
    (cd "${SHARNESS_BUILD_DIRECTORY}" &&
    git push -q -f "${SWUPDATE_PATH}" HEAD:master)
}

# creates a simulated empty remote repo called project
create_project_origin_repo() {
    create_empty_remote_repo "${ORIGIN_PROJECT_PATH}"
}

create_component_repo() {
    create_remote_repo "${COMPONENT_PATH}"
}

create_component2_repo() {
    create_remote_repo "${COMPONENT2_PATH}"
}

create_subcomponent_repo() {
    create_remote_repo "${SUBCOMPONENT_PATH}"
}

create_space_component_repo() {
    create_remote_repo "${SPACE_COMPONENT_PATH}"
}

create_thirdparty_component_repo() {
    create_remote_repo "${THIRDPARTY_COMPONENT_PATH}"
}

create_full_project_repo() {
    create_remote_repo "${FULL_PROJECT_PATH}"
    add_to_remote_repo "${FULL_PROJECT_PATH}" "Added pre-commit hook refusing files ending with a digit." \
        "mkdir -p .githooks/pre-commit && cp -p ${RESOURCE_DIR}/pre-commit-nodigitfiles .githooks/pre-commit/"
    create_component_repo
    create_component2_repo
    create_subcomponent_repo
    create_space_component_repo
    create_thirdparty_component_repo
    add_submodule_to_remote_repo "${COMPONENT_PATH}" "${SUBCOMPONENT_PATH}" "subcomponent"
    add_submodule_to_remote_repo "${FULL_PROJECT_PATH}" "${COMPONENT_PATH}" "component"
    add_submodule_to_remote_repo "${FULL_PROJECT_PATH}" "${COMPONENT2_PATH}" "component2"
    add_submodule_to_remote_repo "${FULL_PROJECT_PATH}" "${SPACE_COMPONENT_PATH}" "space component"
    add_submodule_to_remote_repo "${FULL_PROJECT_PATH}" "${THIRDPARTY_COMPONENT_PATH}" "thirdparty component"
    for repo_dir in "${SUBCOMPONENT_PATH}" "${COMPONENT_PATH}" "${COMPONENT2_PATH}" "${SPACE_COMPONENT_PATH}" "${THIRDPARTY_COMPONENT_PATH}" "${FULL_PROJECT_PATH}"
    do
        create_remote_branch "${repo_dir}" master second_branch
        add_to_remote_repo_branch "${repo_dir}" second_branch "Added second_branch" "echo second_branch > second_branch.txt"
    done
}

# Should be replaces by git project branch when available
make_project_branch() {
    local branch;branch=$1

    git branch -q ${branch}
    git submodule -q foreach --recursive git branch -q ${branch}
}

checkout_project_branch() {
    local branch;branch=$1

    git checkout -q ${branch}
    git submodule -q foreach --recursive git checkout -q ${branch}
}

create_user_installation_using_variables() {
    local dest=$(test -z "$1" || echo "/${1}")
    run_make install KEEP_BUILD_FILES=y DESTDIR="${INSTALL_DIR}${dest}" PREFIX="/local" COMPLETIONPREFIX="/bash" \
        HTMLPREFIX="/html" GITCONFIG=
}

create_user_installation_using_config() {
    run_make install KEEP_BUILD_FILES=y FROM_CONFIG=y GITCONFIG=
}

remove_user_installation_using_variables() {
    local dest=$(test -z "$1" || echo "/${1}")
    run_make uninstall DESTDIR="${INSTALL_DIR}${dest}" PREFIX="/local" COMPLETIONPREFIX="/bash" \
        HTMLPREFIX="/html" GITCONFIG=
}

remove_user_installation_using_config() {
    run_make uninstall FROM_CONFIG=y GITCONFIG=
}

install_sut() {
    test_exec run_make install KEEP_BUILD_FILES=y DESTDIR="${SUT_DIR}" PREFIX="/local" COMPLETIONPREFIX="/bash" \
        HTMLPREFIX="/html" GITCONFIG=
    export MANPATH="$(git config project.install.man):$(manpath)"
    export PATH="$(git config project.install.bin):${PATH}"
}

uninstall_sut() {
    test_exec run_make uninstall DESTDIR="${SUT_DIR}" PREFIX="/local" COMPLETIONPREFIX="/bash" \
        HTMLPREFIX="/html" GITCONFIG=
    rm -rf "${SUT_DIR}"
}

# Create a branch in this module by first branching this module, then
# all submodules and create a new commit with updated tracking
# information if needed (ie if there are sub modules).
# $1 new branch
# $2 commit message
branch_module() {
    local branch
    branch="$1"
    local message
    message="$2"
    local old_ifs
    local repo
    git checkout -b "${branch}"
    git submodule
    old_ifs="$IFS"
    IFS=$'\n'
    for repo in $(git submodule|sed 's/.[^ ]* //;s/ (.*)//')
    do
        (cd "$repo"; branch_module "$branch" "$message")
        git config -f .gitmodules "submodule.${repo}.branch" "$branch"
    done
    IFS="$old_ifs"
    if [[ -n $(git status -s) ]]
    then
        add_to_repo . "$message" ''
    fi
}

# Creates a file and adds it. Assumes CWD is top repo."
# $1 - filename
# [$2 ...] - submodules
create_add_file() {
    local filename; filename="$1"; shift
    if [ $# -gt 0 ]; then
        while [ $# -gt 0 ]; do
            (cd "$1" && touch "${filename}" && git add "${filename}")
            shift
        done
    else
        touch "${filename}" && git add "${filename}"
    fi
}

# [$1 ...] - submodule (default=.)
# returns 0 if nothing to commit in submodule, otherwise 1
nothing_to_commit() {
    local submodules=.
    if [ $# -gt 0 ]; then
        submodules="$@"
    fi
    for submodule in "${submodules}"; do
        (cd "${submodule}" && git diff --cached --exit-code > /dev/null) || return 1
    done
}

# [$1 ...] - submodule (default=.)
# returns 0 if something to commit in submodule, otherwise 1
something_to_commit() {
    ! nothing_to_commit "$@"
}

# $1 - submodule
# $2 - revision
# [$3...] - files to look for
# returns 0 if files exists in diff, otherwise 1
rev_contains_file() {
    local submodule; submodule="$1"; shift
    local rev; rev="$1"; shift
    diff_contains_file "${submodule}" "${rev}"^ "${rev}" "$@"
}

# $1 - submodule
# $2 - start-rev
# $3 - end-rev
# [$4...] - files to look for
# returns 0 if files exists in diff, otherwise 1
diff_contains_file() {
    local submodule; submodule="$1"; shift
    local start_rev; start_rev="$1"; shift
    local end_rev; end_rev="$1"; shift
    if [ ${#@} -gt 0 ]; then
        for f in "$@"; do
            (cd "${submodule}" &&
             ! git diff --name-only --exit-code "${start_rev}" "${end_rev}" -- "$f" > /dev/null) || return 1
        done
    fi
}

# $1 - submodule
# $2 - revision
# $3 - message
rev_has_message() {
    (cd "$1" && test_equal "$(git log --format=%B -n 1 "$2")" "$3")
}

# $1 - submodule
# $2 - revision
# $3 - author
rev_has_author() {
    (cd "$1" && test_equal "$(git log --format=%aN -n 1 "$2")" "$3")
}

# $1 - submodule
# [$2 ...] - files
# returns 0 if all listed files are in the index, otherwise 1
index_contains_file() {
    local submodule; submodule="$1"; shift
    if [ ${#@} -gt 0 ]; then
        for f in "$@"; do
            (cd "${submodule}" &&
             ! git diff --name-only --exit-code --cached -- "$f" > /dev/null) || return 1
        done
    fi
}

# $1 - submodule
# [$2 ...] - files
# returns 0 if any of the listed files are in the index, otherwise 1
index_contains_any_file() {
    local submodule; submodule="$1"; shift
    (cd "${submodule}" && ! git diff --name-only --cached --exit-code -- "$@" > /dev/null)
}

# $1 -submodule
# returns 0 if the index is empty, otherwise 1
index_is_empty() {
    (cd "$1" && git diff --name-only --cached --exit-code > /dev/null)
}

# $1 - submodule
# $2 - revision
# $3 - message
# [$4 ...] - files
verify_commit() {
    local submodule; submodule="$1"; shift
    local start_rev; rev="$1"; shift
    local msg; msg="$1"; shift
    nothing_to_commit "${submodule}" &&
    rev_has_message "${submodule}" "${rev}" "${msg}" &&
    if [ ${#@} -gt 0 ]; then
        rev_contains_file "${submodule}" "${rev}" "$@"
    fi
}



# Check if the first argument is in a list.
# This will check if the first argument is equal to any of the
# other arguments, it can be used to check membership in an array
# is_in_list "an item" "${array[@]}"
# But also
# is_in_list "$item" "possible 1" "possible 2" "third"
is_in_list() {
    local item
    item="$1"
    shift
    local list_element
    for list_element in "${@}"
    do
        [[ "$list_element" == "$item" ]] && return 0
    done
    return 1
}

# Check if a file exists anywhere in the tree.
# $1 - name of file
# $2 - directory to search in
file_exists_anywhere() {
    find "$2" -name "$1" | grep -q -e .
}

# Check if the supplied directory is a git directory
# $1 - name of directory
# Return values:
# 0 - it is indeed a git directory (.git, not a working directory)
# 1 - is is either not a directory or not a directory
is_git_directory() {
    local result
    if [[ -d $1 ]]
    then
        pushd "$1" &>/dev/null
        if [[ "$(git rev-parse --is-inside-git-dir)" == "true" ]]
        then
            result=0
        else
            result=1
        fi
        popd &>/dev/null
    else
        result=1
    fi
    return $result
}

# Compare two git repositories in such as way
# that we verify that ref1 of repo1 is equal
# to ref2 of repo2 for the main repository as
# well as all modules.
# $1 - repo1
# $2 - ref1
# $3 - repo2
# $4 - ref2
# $5 onwards is a list of modules that should not be checked
#
# Return values:
# 0 all refs where equal
# 1 at least one ref differed
# 2 the ref is missing in at least one place
# 128 argument error
# 129 one or both of repo1 and repo2 are not git repositories
# 130 repository layout with regards to modules does not match
# Will not detect if repo2 has extra modules!
compare_all_refs() {
    if [ $# -lt 4 ]
    then
        echo WRONG NUMBER OF ARGUMENTS
        exit 128
    fi
    local repo1
    local repo2
    local ref1
    local ref2
    local -a modules
    repo1="$1"
    shift
    ref1="$1"
    shift
    repo2="$1"
    shift
    ref2="$1"
    shift
    skiplist=("$@")

    if ! ( [[ -d "${repo1}" && -d "${repo2}" ]] &&
            is_git_directory "${repo1}" &&
            is_git_directory "${repo2}" )
    then
        echo NOT GIT REPOSITORY
        exit 129
    fi

    diff -q "${repo1}/${ref1}" "${repo2}/${ref2}" || exit 1

    modules=("${repo1}"/modules/*)
    for module in "${modules[@]}"
    do
        module_base=$(basename "${module}")
        if ! [[ -d "${repo2}/modules/${module_base}" ]]
        then
            echo "MODULE MISMATCH '${repo2}/modules/${module_base}' missing"
            echo "corresponding module is '${module}'"
            exit 130
        fi

        if is_in_list "$module_base" "${skiplist[@]}"
        then
            continue
        fi
        if ! ( [[ -f "${repo1}/modules/${module_base}/${ref1}" && \
                  -f "${repo2}/modules/${module_base}/${ref2}" ]] )
        then
            echo "ONE IS NOT A FILE >${module_base}< >${ref1}< >${ref2}<"
            exit 2
        fi

        diff -q "${repo1}/modules/${module_base}/${ref1}" \
            "${repo2}/modules/${module_base}/${ref2}" || exit 1
    done
}

# Verify that the first reference is the direct offspring of all
# the others.
# Two arguments - linear history and not a merge commit
# Three arguments - a normal merge commit
# Four or more arguments - an octopus merge.
# Order matters!
check_ancestry() {
    local ref
    local actual
    git rev-parse -q --no-revs --verify $1 || return 1
    actual=" $(git rev-list --parents -n 1 $1)"
    local expected
    expected=""
    for ref in "$@"
    do
        expected="${expected} $(git rev-parse --verify -q ${ref})"  || return 1
    done
    [ "${expected}" = "${actual}" ]
}
export -f check_ancestry

# Do check_ancestry for top repository and all listed modules.
# The module list comes first, followed by -- and then the ancestry refs.
# e.g. check_ancestry_recursive component "component 2" -- HEAD branch1 branch2
# See check_ancestry() for details
check_ancestry_recursive() {
    local -a modules
    while [ $# -ne 0 ]
    do
        case $1 in
            --)
            shift
            break
            ;;
            *)
            modules=("${modules[@]}" "$1")
            shift
            ;;
        esac
    done
    check_ancestry "$@"
    for i in "${modules[@]}"
    do
        (cd "$i" && check_ancestry "$@") || return 1
    done
}

# Verify that the submodules are on branch
# $1 - branch
# $2.. - submodules
on_branch() {
    local actual_branch
    local branch
    branch="$1"
    shift
    for repo in "$@"
    do
        [ -d "$repo" ] || return 1
        pushd "${repo}" &>/dev/null
        actual_branch="$(git symbolic-ref -q --short HEAD)"
        popd &>/dev/null
        if [ "$branch" != "${actual_branch}" ]
        then
            echo "'${repo}' is on branch '${actual_branch}' instead of '${branch}'"
            return 1
        fi
    done
    return 0
}

# Verify that the submodules are all configured to follow branch
# $1 - branch
# $2.. - submodules
follows_branch() {
    local branch
    branch="$1"
    shift
    for repo in "$@"
    do
    [ $(git config -f .gitmodules "submodule.${repo}.branch") != "$branch" ] && return 1
    done
    return 0
}

# Do rev parse in a rubmodule
# $1 - Submodule
# $2 - reference
rev_parse_submodule() {
    local submodule; submodule="$1"
    local revision; ref="$2"

    cd "$submodule"
    git rev-parse --verify -q ${ref}
}

# Verify that the commit message is the intended one
# The optional commit identifier is sent to git log, so it
# can be a branch, a commit or even a file.
# $1 - commit message
# $2 - commit identifier
verify_commit_message() {
    if [ $# -ne 2 ]
    then
        echo "Wrong number of arguments to verify_commit_message()"
        exit 99
    fi
    local expected; expected="$1"
    local identifier; identifier="$2"
    local actual; actual=$(git log -1 --pretty=format:"%s" "${identifier}")
    if ! [ "${actual}" = "${expected}" ]
    then
        echo "Wrong commit message for: ${identifier}"
        echo "Got message:"
        echo  "${actual}"
        echo "Expected:"
        echo "${expected}"
        return 1
    else
        return 0
    fi
}

store_state() {
    rsync -a --del .git/ "${SHARNESS_TRASH_DIRECTORY}/before.git"
    test_when_finished "rm -rf \"${SHARNESS_TRASH_DIRECTORY}/before.git\""
}
