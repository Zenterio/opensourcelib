git-project-rebase(1) -- Rebase a project repository
====================================================

## SYNOPSIS

`git-project-rebase` [--abort] [--continue] [-h] [--help] &lt;branch&gt; 

## DESCRIPTION

Rebases all submodules according to the options specified, and lastly the main project repository.
While rebasing, it will try to help out with conflicts in submodules,  and point the parent module
to the rebased version of the submodule.

When other conflicts arise, the user must first resolve the conflicts before continuing with:

NOTE!
git *project* rebase --continue

If you by mistake continue using "git rebase --continue", you *might* be able to continue rebasing using the project
version.

The branch specified as &lt;branch&gt; is the target branch to rebase on top of.

## OPTIONS

  * --abort
    Aborts an ongoing git project rebase.

  * --continue
    Continues an ongoing git project rebase after manually resolving conflicts.

  * -h:
    Print short usage description and exit

  * --help:
    Show this man page and exit


## DETAILS

git-project-rebase performs (very simplified):

  * git submodule foreach git rebase &lt;branch&gt;

  * git rebase &lt;branch&gt;

The rebased commits in the top repo are rewritten to point
to the rebased commits in the subrepos, instead of the old, now invalid, commits.