__git_buildinfo(){
    local lastword=${COMP_WORDS[-1]}
    case "${lastword}" in
        -h|--help|--commands)
            __gitcomp
            return
            ;;
    esac
    local default="-h --help --commands $(git buildinfo --commands)"
    __gitcomp "$default"
}

_git_buildinfo(){
    if [ ${COMP_CWORD} -ge 3 ]; then
        local projcmd=${COMP_WORDS[2]}
        local e
        for e in $(git buildinfo --commands); do
            if [ "$e" = "$projcmd" ]; then
                _git_buildinfo_${projcmd}
                return
            fi
        done
        __git_buildinfo
        return
    else
        __git_buildinfo
        return
    fi
}

