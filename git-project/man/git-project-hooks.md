git-project-hooks(1) -- A tool to manage project, user, and global Git hooks for multiple git repositories.
===========================================================================================================

## SYNOPSIS

`git-project-hooks` [--install|--uninstall]

## DESCRIPTION

git-project-hooks lets hooks be installed inside git repositories, users home directory, and globally.
When a hook is called by `git`, git-project-hooks will check each of these locations for the hooks to run.

Please use `git help githooks` for more info about hooks in git.

## OPTIONS

  --install

Tells the repository to use git-project-hooks hooks.

  --uninstall

Revert to your previous hooks.


Running git project hooks with no argument lists the currently installed hooks.

## EXAMPLES

  Install hooks:

    $ git project hooks --install


  List currently installed hooks:

    $ git project hooks

