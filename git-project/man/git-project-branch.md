git-project-branch(1) -- Create a branch
========================================

## SYNOPSIS

`git-project-branch` [-h] [--help] [&lt;branch&gt;] [&lt;subrepo&gt;...]

## DESCRIPTION

This command till create and checkout a branch in the top repository
and the selected subrepositories. The default is to create the branch
for all subrepositories.

If already on the branch, it will do nothing which makes it possible
to add subrepositories to a branch.

If the branch exists and is not checked out in any of the
repositories, git project branch will exit with an error.

git-project-branch will also update the tracking information in the
top repository.

Contrary to 'git branch', 'git project branch' will check out the
created branch.

## OPTIONS

  * -h:
    Show short usage description and exit.

  * --help:
    Show this man page and exit.

## EXAMPLES

Create a topic branch for FOO issue 47 in the whole project.

    git project branch topic-FOO-47

Create a topic branch for FOO issue 47 for the sub repo src/component in this project.

    git project branch topic-FOO-47 src/component

## DETAILS
git-project-branch performs:

  * git checkout -b:
    Used to create and check out branches.
  * git project config:
    Used to change the tracking information.
