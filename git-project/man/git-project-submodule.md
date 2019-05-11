git-project-submodule(1) -- Manage submodules
=============================================

## SYNOPSIS

`git-project-submodule` [-h] [--help] [&lt;OPTIONS&gt;] [subrepos]

## DESCRIPTION
Command group for managing submodules.

## OPTIONS

  * -h:
    Show short usage description and exit.

  * --help:
    Show this man page and exit.

  * -b, --branch branch:
    Change branch to track.

  * -u, --update:
    Update repository as well.

## EXAMPLES

git-project-submodule --branch new_branch --update module_1 module_2

  * Will change the branch for module_1 and module_2 to "new_branch"
  * Will update so that the latest commit on new_branch in the remote
    repository is used.

git-project-submodule --branch new_branch module

  * Will change the branch for module to "new_branch"
  * Will not update you work space or what commit is used.

## DETAILS

 * Uses git config to update the .gitmodules file
 * If updating:
 * git submodule init &lt;module&gt;
 * git submodule update --remote &lt;module&gt;
