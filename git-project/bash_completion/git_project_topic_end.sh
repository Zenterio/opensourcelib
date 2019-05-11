_git_project_topic_end(){
    if [ ${COMP_CWORD} -eq 3 ] || \
        [ ${COMP_CWORD} -eq 4 -a "${COMP_WORDS[2]}" == "topic" ] ; then
        __gitcomp "-h --help $(__git_refs '' 1|grep '^topic-')"
    fi
    return
}
