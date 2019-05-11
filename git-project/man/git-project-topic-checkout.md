git-project-topic-checkout(1) -- Checkout a topic branch
========================================================

## SYNOPSIS

`git-project-topic-checkout` [-h] [--help]

`git-project-topic-checkout` [-q|--quiet] [-f|--force] &lt;branch&gt;

## DESCRIPTION

This command will check out a topic branch in the top repository and
in all the sub repositories that are on that branch. It will update
all other sub repositories to the corresponding commit in detached
HEAD.

## OPTIONS

  * -h:
    Show short usage description and exit.

  * --help:
    Show this man page and exit.

  * -q --quiet:
    Suppress progress reporting.

  * -f --force:
    Force checkout (throw away local modifications).

## EXAMPLES

Checkout a topic branch:

  * git project topic checkout topic-workitem
  * git project topic checkout workitem

## DETAILS

git-project-topic-checkout performs:

  * git project checkout
  * git checkout in relevant submodules.
