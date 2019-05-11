_git_project_topic_checkout(){
    if [ ${COMP_CWORD} -eq 3 ] || \
        [ ${COMP_CWORD} -eq 4 -a "${COMP_WORDS[2]}" == "topic" ] ; then
            __gitcomp "-h --help --force --quiet $(__git_refs '' 1|grep '^topic-')"
    fi
    if [ ${COMP_CWORD} -eq 4 ] || \
        [ ${COMP_CWORD} -eq 5 -a "${COMP_WORDS[2]}" == "topic" ] ; then
        case "$prev" in
            --force|-f)
                __gitcomp "--quiet $(__git_refs '' 1|grep '^topic-')"
                return
                ;;
            --quiet|-q)
                __gitcomp "--force $(__git_refs '' 1|grep '^topic-')"
                return
                ;;
        esac
    fi
    if [ ${COMP_CWORD} -eq 5 ] || \
        [ ${COMP_CWORD} -eq 6 -a "${COMP_WORDS[2]}" == "topic" ] ; then
        case "$prev" in
            --force|-f|--quiet|-q)
                __gitcomp "$(__git_refs '' 1|grep '^topic-')"
                return
                ;;
        esac
    fi
    return
}
