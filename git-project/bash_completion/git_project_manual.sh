_git_project_manual(){
    if [ ${COMP_CWORD} -le 3 ]; then
        __gitcomp "-h --help"
    else
        __gitcomp ""
    fi
}