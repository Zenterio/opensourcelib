_git_buildinfo_checkout(){
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    if [[ ${COMP_CWORD} -le 3 && ${cur} == -* ]]; then
        __gitcomp "-b -h --help --no-clone --checkout-branch"
    fi
}
