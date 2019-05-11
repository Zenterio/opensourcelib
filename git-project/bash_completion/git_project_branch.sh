_git_project_branch(){
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    if [[ ${COMP_CWORD} -le 3 && ${cur} == -* ]]; then
        __gitcomp "-h --help"
    elif [[ ${COMP_CWORD} -gt 3 ]]; then
        __gitcomp "$(git project --submodules)"
    fi
}
