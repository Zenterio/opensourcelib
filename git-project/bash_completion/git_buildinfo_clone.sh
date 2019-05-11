_git_buildinfo_clone(){
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    if [[ ${COMP_CWORD} -le 3 && ${cur} == -* ]]; then
        __gitcomp "-c -h --help --checkout-commit"
    fi
}
