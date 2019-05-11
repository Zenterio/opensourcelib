git-project-checkout(1) -- Checkout a branch
============================================

## SYNOPSIS

`git-project-checkout` [-h] [--help]
`git-project-checkout` [options] &lt;branch&gt;

## DESCRIPTION

This command will check out a branch, tag or other valid reference in
the top repository and update all sub repositories to the
corresponding commit.

## OPTIONS

  * -h:
    Show short usage description and exit.

  * --help:
    Show this man page and exit.

  * -q --quiet:
    Suppress progress reporting.

  * --detach:
    Detach HEAD in master repository.

  * -f --force:
    Force checkout (throw away local modifications).

## EXAMPLES

  * Checkout a release build from tag:
    git project checkout RELEASE_1_2

  * Checkout the latest on the master branch:
    git project checkout master

## DETAILS
git-project-checkout performs:

  * git checkout
  * git submodule sync
  * git submodule init --update
