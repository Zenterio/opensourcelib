git-project-sw-update(1) -- Update git-project installation
===========================================================

## SYNOPSIS

`git-project-sw-update` [-h] [--help] [p,--print-repo]
[-r,--repo=&lt;path-to-repo&gt;] [-u,--user-install]

## DESCRIPTION

Updates the git-project installation to latest available version.

## OPTIONS

  * -h:
    Print short usage description and exit

  * --help:
    Show this man page and exit

  * -p, --print-repo:
    Print the update repo used and exit

  * -r, --repo=&lt;path-to-repo&gt;:
    Update from the repository path specified instead of project configuration

  * -u, --user-install:
    Use this option if it is a user installation.

The repository used by default is configured in gits configuration:
`git config project.update-repo`

It is located in the system configuration by default, global configuration
in case of user-installation.
