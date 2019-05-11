git-project-config(1) -- Manage git project related options
===========================================================

## SYNOPSIS

`git project config` [-h]

`git project config` [--help]

`git project config` [&lt;file-option&gt;] [-z|--null] -l | --list

## DESCRIPTION

You can list all git project related options similar to how `git
config` would do it. It will list all the options from the project
section. To set variables and do more advanced filtering, use `git
config` directly.

Please be aware that `git project config -l` uses `git config
--get-regexp` which does not give exactly the same output as `git
config -l`.

The values are read from the system, global and
repository local configuration files by default, and options *--system*,
*--global*, *--local* and *--file &lt;filename&gt;* can be used to tell the
command to read from only that location (see the section called
[FILES])

This command will fail with non-zero status upon error

 * bad parameters, usage error (ret=129)
 * for other error codes, see git config

On success, the command returns the exit code 0.

## OPTIONS

  * -h:
    Print short usage description and exit

  * --help:
    Show this man page and exit

  * --global:
    Read only from global ~/.gitconfig and from
    $XDG_CONFIG_HOME/git/config rather than from all available files.

    See also the section called [FILES].

  * --system:
    Read only from system-wide $(prefix)/etc/gitconfig rather than
    from all available files.

    See also the section called [FILES].

  * --local:
    Read only from the repository .git/config rather than from all
    available files.

    See also the section called [FILES].

  * -f config-file, --file config-file:
    Use the given config file instead of the one specified by
    GIT_CONFIG.

  * --blob blob:
    Similar to --file but use the given blob instead of a file. E.g.
    you can use *master:.gitmodules* to read values from the file
    *.gitmodules* in the master branch. See "SPECIFYING REVISIONS"
    section in `gitrevisions(7)` for a more complete list of ways to
    spell blob names.

  * -l, --list:
    List all variables set in the project section of the config
    file(s).

  * -z, --null:
    For all options that output values and/or keys, always end values
    with the null character (instead of a newline). Use newline
    instead as a delimiter between key and value. This allows for
    secure parsing of the output without getting confused e.g. by
    values that contain line breaks.

  * --[no-]includes:
    Respect include.* directives in config files when looking up
    values. --no-includes is default, despite what `man git-config`
    claims.

## FILES
See the documentation for git config on how configuration files are
chosen.

## ENVIRONMENT
See the documentation for git config on environmental variables.

## VARIABLES
This list should be a comprehensive and complete list of all git
project related variables.

  * project.dev.*:
    These variables are related to the development environment.
    They will be handled by `make dev-install` and should not be changed.

  * project.install.*:
    These variables store installation parameters and are set during
    `make install`. They should not be changed.

  * project.template:
    Git url to project template, used by `git project init`.

  * project.update-repo:
    Git url to original repository, used by `git project sw-update`.
    (Should this be project.install.update-repo?)

## DETAILS
git-project-config -l|--list performs:

  * git config --get-regexp project[.].*

## SEE ALSO
As `git config` is run in the background, see that documentation for
details on what configuration files and environment variables are used.

## COPYRIGHT INFORMATION
Much of this text was copied verbatim or with small modifications from
the man page of `git config`.
