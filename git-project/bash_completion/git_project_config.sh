_git_project_config(){
    local lastword=${COMP_WORDS[-2]}
    case "${lastword}" in
        -h|--help)
            __gitcomp
            return
            ;;
        -f|--file)
            _filedir
            return
            ;;
        --blob)
            __git_complete_remote_or_refspec
            return
    esac
    __gitcomp "-h --help --global --system --local -f --file --blob -l --list -z --null --no-includes --includes --testmode"
    return
}
