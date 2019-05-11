_git_project_sw-update(){
    if [ ${COMP_CWORD} -le 4 ]; then
        local lastword=${COMP_WORDS[-2]}
        case "${lastword}" in
            -h|--help|-p|--print-repo)
                __gitcomp
                return
                ;;
            -u|--user-install)
                __gitcomp "-r --repo"
                return
                ;;
            -r|--repo)
                __gitcomp "-u --user-install"
                return
                ;;
        esac
        __gitcomp "-h --help -p -r -u --print-repo --repo --user-install"
        return
    else
        __gitcomp ""
    fi
}

