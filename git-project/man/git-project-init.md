git-project-init(1) -- Create Git Project
=========================================

## SYNOPSIS

`git-project-init` [-h] [--help] [-n,--no-hooks] [-o,--origin]
[-p,--print-template] [-t,--template=&lt;template&gt;] [&lt;directory&gt;]

## DESCRIPTION

Creates an empty git project repository from the template specified in project configuration.
If directory is left out, current directory is used.
Installs git hooks unless avoided by --no-hooks switch.
Please see `git help hooks` for more information about git hooks.

## OPTIONS

  * -n,--no-hooks:
    Do not install hooks for the inited repo

  * -o,--origin:
    Specify a remote orgin repository to be setup at start

  * --print-template:
    Print the current configured template and exit

  * -t, --template=&lt;template&gt;:
    Use the repository path specified instead of project configuration


The repository used by default is configured in git's configuration:
`git config project.template`

It is located in the system configuration by default, global configuration
in case of user-installation.

## DETAILS

git-project-init performs:

  * git clone TEMPLATE .
  * git submodule init
  * git remote remove origin
  * git submodule update --init --recursive
  * git remote add origin ORIGIN
  * git hooks --install  (Unless avoided by --no-hooks switch)
