git-project-clone(1) -- Clone a project repository
==================================================

## SYNOPSIS

`git-project-clone` [-h] [--help] [-n,--no-hooks] [&lt;OPTIONS&gt;]

## DESCRIPTION

Clones the project repository and performs needed initialization.
Installs git hooks unless avoided by --no-hooks switch.
Please see `git help hooks` for more information about git hooks.

## OPTIONS

  * -h:
    Print short usage description and exit

  * -n,--no-hooks:
    Do not install hooks for the cloned repo

  * --help:
    Show this man page and exit

  git-project-clone supports the same options as _git clone_.

## DETAILS

git-project-clone performs:

  * git clone --recursive-submodules REPO [DIR]

  If hooks is not prohibited by -n option:

  * git project hooks --install
