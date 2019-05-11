_git_project_hooks(){
   if [ ${COMP_CWORD} -le 3 ]; then
        __gitcomp "-h --help --install --uninstall"
    else
        __gitcomp ""
    fi
}
