_git_project_checkout(){
    if [ ${COMP_CWORD} -eq 2 ] || \
        [ ${COMP_CWORD} -eq 3 -a "${COMP_WORDS[1]}" == "project" ] ; then
        __gitcomp "--help --quiet --detach --force $(__git_refs '' 1)"
    fi
}
