__git_project(){
    local lastword=${COMP_WORDS[-2]}
    case "${lastword}" in
        -h|--help|-v|--version|--commands|--guides|--submodules)
            __gitcomp
            return
            ;;
    esac
    local default="-h --help -v --version --sw-update --commands --guides --submodules --all-submodules $(git project --commands)"
    __gitcomp "$default"
}

_git_project(){
    if [ ${COMP_CWORD} -ge 3 ]; then
        local projcmd=${COMP_WORDS[2]}
        if [ "${projcmd}" = "--sw-update" ]; then
            _git_project_sw-update
            return
        else
            local e
            for e in $(git project --commands); do
                if [ "$e" = "$projcmd" ]; then
                    _git_project_${projcmd}
                    return
                fi
            done
            __git_project
            return
        fi
    else
        __git_project
        return
    fi
}

