_git_project_submodule(){
    local lastword=${COMP_WORDS[-2]}
    local submodules
    mapfile -t submodules < <( git project --submodules)
    case "${lastword}" in
        -h|--help)
            __gitcomp
            return
            ;;
        -b|--branch)
            __gitcomp_nl "$(__git_refs '' 1)"
            return
            ;;
        -u|--update)
            __gitcomp "-b --branch ${submodules}"
            return
    esac
    __gitcomp "-h --help -b --branch -u --update ${submodules}"
    return
}
