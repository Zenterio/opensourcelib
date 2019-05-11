git-project-commit(1) -- Commit a project repository
====================================================

## SYNOPSIS

`git-project-commit` [options] [submodule ...]

## DESCRIPTION

Commits any staged files in the submodules and commits the new version of
changed submodules in the project repository along with any staged files on
top level.

Submodules will only be added to the top repository if they had staged but
uncommitted content. It is not enough to be on an updated commit.

If submodules are listed, only these and the top repository will be affected.
If no submodules are listed all submodules will be included in the commit.

If one of the submodules fails to commit, or if the top module fails to commit,
the commits completed in the submodules are reverted.

Any options used will affect all commits. Hence using --amend will amend to the
last commit in all submodules and in the top repository.

`git-project-commit` supports most of the options available for `git commit`.

## OPTIONS

`See git-commit(1) for details.`

  * -h:
    Show short usage description and exit

  * --help:
    Show this man page and exit

  * -q, --quiet:
    Suppress output

  * -v, --verbose:
    Show diff in commit message template

###Commit message options

  * -F, --file &lt;file&gt;:
    Read message from file

  * --author &lt;author&gt;:
    Override author for commit

  * --date &lt;date&gt;:
    override date for commit

  *  -m, --message &lt;message&gt;:
    Commit message

  * -c, --reedit-message &lt;commit&gt;:
    Reuse and edit message from specified commit

  * -C, --reuse-message &lt;commit&gt;:
    Reuse message from specified commit

  * --fixup &lt;commit&gt;:
    Use autosquash formatted message to fixup specified commit

  * --squash &lt;commit&gt;:
    Use autosquash formatted message to squash specified commit

  * --reset-author:
    The commit is authored by me now (used with -C/-c/--amend)

  * -s, --signoff:
    Add Signed-off-by

  * -t, --template &lt;file&gt;:
    Use specified template file

  * -e, --edit:
    Force edit of commit

  * --cleanup &lt;default&gt;:
    How to strip spaces and #comments from message

  * --status:
    Include status in commit message template

  * -S, --gpg-sign[=&lt;key id&gt;]:
    GPG sign commit

### Commit contents options

  * -a, --all:
    Commit all changed files

  * --interactive:
    Interactively add files

  * -p, --patch:
    Interactively add changes

  * -n, --no-verify:
    Bypass pre-commit hook

  * --dry-run:
    Show what would be committed

  * --short:
    Show status concisely

  * --branch:
    Show branch information

  * --porcelain:
    Machine-readable output

  * --long:
    Show status in long format (default)

  * -z, --null:
    Terminate entries with NUL

  * --amend:
    Amend previous commit

  * --no-post-rewrite:
    Bypass post-rewrite hook

  * -u, --untracked-files[=&lt;mode&gt;]:
    Show untracked files, optional modes: all, normal, no. (Default: all)

## EXAMPLES

Standard use case:

    git project commit --message "your message"

## DETAILS
git-project-commit performs:

  * git commit in all submodules
  * git add submodule for all submodules with newly created commits
  * git commit in top repository
  * in case of failure, revert by git reset --soft HEAD^
