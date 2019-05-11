git-project-topic-begin(1) -- start work on a topic
===================================================

## SYNOPSIS

`git-project-topic-begin` [-h]

`git-project-topic-begin` [--help]

`git-project-topic-begin` &lt;topic-branch&gt; [&lt;submodule&gt;...]

## DESCRIPTION

This command will create and check out a topic branch and one or more submodules.

A branch with the same name will be created and checked out in the top repository as well as the listed submodules
(if no submodules are listed all submodules will be checked out on the new topic branch).

The name of the topic branch must begin with topic- and the topic- prefix will be added if omitted.

The command will not affect submodules of submodules.

## OPTIONS

  * -h:
    Show short usage description and exit.

  * --help:
    Show this man page and exit.

## EXAMPLES

Create a new topic branch name topic-workitem:

    git project topic begin workitem
    git project topic begin topic-workitem

## DETAILS:
gitproject-topic-begin will call:

  * git project branch topic-branch [modules...]
