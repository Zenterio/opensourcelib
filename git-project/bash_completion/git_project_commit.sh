

_git_project_commit(){
    case "$prev" in
    -c|-C)
        __gitcomp_nl "$(__git_refs)" "" "${cur}"
        return
        ;;
    esac

    case "$cur" in
    --cleanup=*)
        __gitcomp "default strip verbatim whitespace
            " "" "${cur##--cleanup=}"
        return
        ;;
    --reuse-message=*|--reedit-message=*|\
    --fixup=*|--squash=*)
        __gitcomp_nl "$(__git_refs)" "" "${cur#*=}"
        return
        ;;
    --untracked-files=*)
        __gitcomp "all no normal" "" "${cur##--untracked-files=}"
        return
        ;;
    -*)
        __gitcomp "
            --all --author= --date= --signoff --no-verify
            --edit --no-edit --status --gpg-sign=
            --amend --only --interactive --patch --short --porcelain
            --long --null --no-post-rewrite
            --dry-run --reuse-message= --reedit-message=
            --reset-author --file= --message= --template=
            --cleanup= --untracked-files --untracked-files=
            --verbose --quiet --fixup= --squash=
            "
        return
    esac

    __gitcomp_nl "$(git project --submodules)"

}
