git-buildinfo(1) -- git buildinfo's manual page
===============================================

## SYNOPSIS

`git-buildinfo` [--commands] [-h] [--help] [&lt;command&gt;]

## DESCRIPTION

Utility to manage build-info in git repositories.

## OPTIONS

  * --commands:
    Print the available commands.

  * -h:
    Show short usage description and exit.

  * --help:
    Show this man page and exit.

  * --web:
    Display manual page for the command or guide in html format, in a browser.

## COMMON GIT BUILDINFO COMMANDS

   - **git-buildinfo-status(1)** Show status in build-info format
   - **git-buildinfo-checkout(1)** Checkout repositories to match build-info file
   - **git-buildinfo-clone(1)** Clone repositories to match build-info file

For a full list of commands, run `git buildinfo --commands`

## BUILD-INFO FORMAT

    Time: YYYY-MM-DD HH:mm:ss+TimeZone
    Job: TEXT Job name
    Build: INT build-identifer
    External build number: INT secondary build-identifier
    URL: URL reference to build
    Build node: TEXT build node information
    Origin: TEXT source code context
    -------------------------------------------------
    Repository: TEXT repository name
    Remote: git-remote
    Branch: branch name
    Commit: SHA-1
    Message:
    TEXT commit message
    -------------------------------------------------
    Next repository
