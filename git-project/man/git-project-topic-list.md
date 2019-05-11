git-project-topic-list(1) -- List topic branches 
================================================

## SYNOPSIS

`git-project-topic-list` [-h] [--help] [-a|--all] [-r|--remote]

## DESCRIPTION

List topics, with --remote or --all list known remote topics.

It will also list what subrepositories are affected by the topic.

## OPTIONS

  * -h:
    Show short usage description and exit.

  * --help:
    Show this man page and exit.

  * -r, --remote:
    List topic branches in remote repository only.

  * -a, --all:
    List topic branches in remote and local repository.

## EXAMPLES

In this case topic-task is available both remotely and locally, while
topic-task2 is only in the local repository. There is a third task,
topic-task-remote that has not been checked out locally.

      # git project topic list
      topic-task ('module A', 'module B')
      topic-task2 ('module B', 'module C')

      # git project topic list -r
      origin/topic-task ('module A', 'module B')
      origin/topic-task-remote ('module F')

      # git project topic list -a
      topic-task ('module A', 'module B')
      topic-task2 ('module B', 'module C')
      origin/topic-task ('module A', 'module B')
      origin/topic-task-remote ('module F')

Notice that "topic-task" is listed twice when using -a, once as a
local topic and once as the remote origin/topic-task.

## DETAILS

git-project-topic-list uses git for-each-ref to find out what branches exist:

  * git for-each-ref --format='%(refname)' refs/heads 
  * git for-each-ref --format='%(refname)' refs/remotes/origin 

