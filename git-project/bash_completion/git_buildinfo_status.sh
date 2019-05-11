_git_buildinfo_status(){
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    if [[ ${COMP_CWORD} -le 3 && ${cur} == -* ]]; then
        __gitcomp "-h --help --save"
    fi
}
