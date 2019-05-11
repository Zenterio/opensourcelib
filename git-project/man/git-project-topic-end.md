git-project-topic-end(1) -- end work on a topic
=========================================

## SYNOPSIS

`git-project-topic-end` [-h]

`git-project-topic-end` [--help]

`git-project-topic-end` &lt;topic-branch&gt; &lt;message&gt;

## DESCRIPTION

This command will end work on a topic by merging the topic-branch to the currently checked out branch.

## OPTIONS

  * -h:
    Show short usage description and exit.

  * --help:
    Show this man page and exit.

## EXAMPLES

    git project topic end topic-FOO "commit message"

## DETAILS
git-project-topic-end topic-foo first checks out the target branch in all sub repositores,
and verifies that things are likely up to date, followed by:

  * git project merge topic-foo "commit message"
