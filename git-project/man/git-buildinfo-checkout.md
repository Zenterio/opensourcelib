git-buildinfo-checkout(1) -- Checkout repository based on build-info file
=========================================================================

## SYNOPSIS

`git-buildinfo-checkout` [-h] [--help] [--no-clone] [-b, --checkout-branch] FILE|URL

## DESCRIPTION

Checks-out a set of existing git repositories based on a build-info file.
New repositories may be cloned if missing. The command must be run in the
top repository, corresponding to the first repository in the build-info file.

## OPTIONS

  * -h:
    Print short usage description and exit

  * --help:
    Show this man page and exit

  * --no-clone:
    Prevents missing repositories from being created (cloned).

  * FILE:
    Path to a build-info file (e.g. `build-info.txt`).

  * URL:
    URL to where a build-info file can be downloaded from. Requires `curl`.
