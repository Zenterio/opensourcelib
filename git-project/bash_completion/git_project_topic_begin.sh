_git_project_topic_begin(){
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    if [[ ${COMP_CWORD} -le 4 && ${cur} == -* ]]; then
        __gitcomp "-h --help"
    elif [[ ${COMP_CWORD} -gt 4 ]]; then
        __gitcomp "$(git project --submodules)"
    fi
}
