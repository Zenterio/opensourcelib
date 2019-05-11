_git_project_init(){
    if [ ${COMP_CWORD} -le 4 ]; then
        local lastword=${COMP_WORDS[-2]}
        case "${lastword}" in
            -h|--help|-p|--print-template)
                __gitcomp
                return
                ;;
            -o|--origin)
                __gitcomp "-t --template"
                return
                ;;
            -t|--template)
                __gitcomp "-o --origin"
                return
                ;;
        esac
        __gitcomp "-h --help -t -o -p --origin --print-template --template"
        return
    else
        __gitcomp ""
    fi
}