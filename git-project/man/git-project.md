git-project(1) -- git project's manual page
===========================================

## SYNOPSIS

`git-project` [--commands] [--guides] [-h] [--help] [--sw-update] [-v] [--version] [&lt;command&gt;]

## DESCRIPTION

Utility to manage complex projects in git.

An overview of git project is available on `git help gitproject-userguide`.

## OPTIONS

  * --commands:
  Print the available commands.

  * --guides:
  Print the available guides.

  * -h:
  Print usage. This option can also be used for any of the project commands.

  * --help:
  Show this help. This option can also be used for any of the project commands.

  * --submodules:
  Print list of top level submodules

  * --all-submodules:
  Print list of all submodules

  * --sw-update:
  Update git-project installation with latest version.
  Alias to `git project sw-update`.

  * -v:
  Print git-project's version number.

  * --version:
  Print git-project's version string.

## COMMON GIT PROJECT COMMANDS

   - **git-project-clone(1)** Clone a git project repository
   - **git-project-init(1)** Create a git project repository
   - **git-project-status(1)** Print status
   - **git-project-sw-update(1)** Update installation with latest version of git-project

For a full list of commands, run `git project --commands`

## ADDITIONAL COMMANDS

  Additional commands also installed but not part of the git-project namespace.

   - **git-summary(1)** Show repository summary
   - **git-hooks(1)** Manage git hooks
