_git_project_topic_delete(){
    if [ ${COMP_CWORD} -eq 3 ] || \
        [ ${COMP_CWORD} -eq 4 -a "${COMP_WORDS[2]}" == "topic" ] ; then
            __gitcomp "-h --help --local --force $(__git_refs '' 1|grep '^topic-')"
    fi
    if [ ${COMP_CWORD} -eq 4 ] || \
        [ ${COMP_CWORD} -eq 5 -a "${COMP_WORDS[2]}" == "topic" ] ; then
        case "$prev" in
            --force|-f)
                __gitcomp "--local $(__git_refs '' 1|grep '^topic-')"
                return
                ;;
            --local|-l)
                __gitcomp "--force $(__git_refs '' 1|grep '^topic-')"
                return
                ;;
        esac
    fi
    if [ ${COMP_CWORD} -eq 5 ] || \
        [ ${COMP_CWORD} -eq 6 -a "${COMP_WORDS[2]}" == "topic" ] ; then
        case "$prev" in
            --force|-f|--local|-l)
                __gitcomp "$(__git_refs '' 1|grep '^topic-')"
                return
                ;;
        esac
    fi
    return
}
