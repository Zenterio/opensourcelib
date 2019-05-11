git-project-merge(1) -- merge branches
======================================

## SYNOPSIS

`git-project-merge` &lt;option&gt;

`git-project-merge` &lt;branch&gt; &lt;message&gt;

## DESCRIPTION

Merge `branch` on to currently checked out branch for each
subrepository that has `branch`.

Commits created will use the supplied message as commit message, which
is mandatory.

`git-project-merge` will update the tracking branch for all sub
repositories to track the upstream branch that is currently checked
out. It will assume that branch names are identical in the current
repository and upstream.

## OPTIONS

  * --abandon:
    Abandon a merge without restoring state. Use this only if you are
    ok with having mixed states in your repositories or the merge has
    failed particularly bad and is now confused about the state of
    your repositories. This only makes sense after git project merge
    has halted because of conflicts.

  * --abort:
    Abort a merge and try to reset original state.
    When a merge has been halted because of a conflict and you do not
    want to resolve the conflicts, this will try to restore all
    repositories to the state before you started the merge.

  * --continue:
    Continue merge after conflict resolution.
    When a merge is halted because of conflicts, you need to resolve
    those conflicts and commit the changes just as for a normal merge
    in that repository.
    However, git project uses sub repositories in a very specific way,
    so you need to run `git project merge --continue` to finish
    merging the rest of the repositories.

  * -h:
    Show short usage description and exits

  * --help:
    Show this man page and exits

## EXAMPLES

git project merge topic-ABC-123 "ABC-123: ABC-123 is ready to be published"

## DETAILS

This command will merge the subrepositories first, and then merge the
top repository. It will also figure out if the source branch has a
different namne in a subrepo then in the top repo, which is not
reflected here.
  * `git submodule foreach git merge -m "${message}" "${source}"`
  * `git commit` the sub repository changes into the current (target) branch in the toprepo.
  * `git merge -m "${message}" "${source}"`
  * Restore the tracking information in .gitmodules that was probably changed by the merge.

There are a few more complex operations done "in the background" to
create the illusion of one repository on one branch, even if there are
several repositories each with its own branch names.
