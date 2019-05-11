git-project-status(1) -- Show project status
============================================

## SYNOPSIS

`git-project-status` [-h] [--help]

## DESCRIPTION

Prints the status of the project and its components.

## OPTIONS

  * -h:
    Print short usage description and exit

  * --help:
    Show this man page and exit

## DETAILS

git-project-status performs:

from the top project directory:

  * git status
  * git submodule foreach 'git status'
