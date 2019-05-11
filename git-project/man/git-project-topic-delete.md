git-project-topic-delete(1) -- delete a topic branch
====================================================

## SYNOPSIS

`git-project-topic-delete` [-h]

`git-project-topic-delete` [--help]

`git-project-topic-delete` [-l|--local] [-f|--force] &lt;topic-branch&gt;

## DESCRIPTION

This command will attempt to verify that the topic you want do delete
has been merged in your local repositories (unless --force is used).

It will delete the topic-branch locally as well as in the remote repositories
for all subrepositories (unless --local is used, if so remote branches are not deleted). 

The --local and --force flags may be combined.

* The command will only delete branches whose name starts with topic-.
* It is possible to leave out the topic- prefix of the branch name (it will be added if not present).
* It will only delete branches that have the same name in the subrepository as in the toprepository, ie are "on the same topic".

The branch to be deleted may not be checked out anywhere.

## OPTIONS

  * -h:
    Show short usage description and exit.

  * --help:
    Show this man page and exit.

  * -l, --local:
    Only delete branches in your local repositories, leave upstream repositories unchanged.

  * -f, --force:
    Delete the branches even if it is not "safe" to do so.

## EXAMPLES

Standard use case:

    git project topic delete topic-name

Drop your local topic branches, even if they are not merged:

    git project topic delete --force --local topic-name

## DETAILS

git-project-topic-delete performs these commands in all affected
subrepositories:

    git branch -d <topic-branch>
    git push :<topic-branch>
