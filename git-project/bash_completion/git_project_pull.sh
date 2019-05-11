_git_project_pull(){
    if [ ${COMP_CWORD} -le 3 ]; then
        __gitcomp "-h --help -m --rebase"
    else
        __gitcomp ""
    fi
}