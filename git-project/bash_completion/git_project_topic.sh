__git_project_topic(){
    local lastword=${COMP_WORDS[-2]}
    case "${lastword}" in
        -h|--help|--commands)
            __gitcomp
            return
            ;;
    esac
    local default="-h --help --commands $(git project topic --commands)"
    __gitcomp "$default"
}

_git_project_topic(){
    if [ ${COMP_CWORD} -ge 4 ]; then
        local projcmd=${COMP_WORDS[3]}
        local e
        for e in $(git project topic --commands); do
            if [ "$e" = "$projcmd" ]; then
                _git_project_topic_${projcmd}
                return
            fi
        done
        __git_project_topic
        return
    else
        __git_project_topic
        return
    fi
}

