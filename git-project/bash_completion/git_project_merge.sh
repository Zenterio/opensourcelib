_git_project_merge(){
    if [ ${COMP_CWORD} -eq 2 ] || \
        [ ${COMP_CWORD} -eq 3 -a "${COMP_WORDS[1]}" == "project" ] ; then
        __gitcomp "-h --help --abandon --abort --continue $(__git_refs '' 1)"
    fi
    return
}
