_git_project_help(){
    if [ ${COMP_CWORD} -le 3 ]; then
        __gitcomp "-g --guides -h --help --web $(git project --commands) $(git project --guides)"
        return
    elif [ ${COMP_CWORD} -le 4 ]; then
        local lastword=${COMP_WORDS[-2]}
        case "${lastword}" in
            --web)
                __gitcomp "$(git project --commands) $(git project --guides)"
                return
                ;;
            -h|--help|-g|--guides)
                return
                ;;
            *)
                __gitcomp "--web"
                return
                ;;
        esac
    fi
}