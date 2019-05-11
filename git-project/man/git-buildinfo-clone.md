git-buildinfo-clone(1) -- Clone repository based on build-info file
===================================================================

## SYNOPSIS

`git-buildinfo-clone` [-h] [--help] [-c,--checkout-commit] FILE|URL

## DESCRIPTION

Clones a set of git repositories based on a build-info file and checks out the
listed branches.

## OPTIONS

  * -h:
    Print short usage description and exit

  * --help:
    Show this man page and exit

  * FILE:
    Path to a build-info file (e.g. `build-info.txt`).

  * URL:
    URL to where a build-info file can be downloaded from. Requires `curl`.

   * -c, --checkout-commit:
    Checks out the commits specified in the build-info file. Leaves the repositories in detached head.