_git_project_topic_list(){
    if [ ${COMP_CWORD} -le 4 ]; then
        __gitcomp "-h --help -a --all -r --remote"
    else
        __gitcomp ""
    fi
}
