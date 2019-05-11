# GIT Project


## INTRODUCTION

Git-project is just a wrapper to basic git commands to simplify everyday
tasks working with a source code based component model.

At its heart, git-project is just git submodules. That's it.

Git-project wraps complex or multiple commands into easy to use and well
documented single commands that can be used for every day tasks and supports
a robust work flow of short lived topic branches for contributing in small
manageable code changes.

### Components

Git-project's main purpose is to make it easy to work with a
`source code based component model`, a.k.a. submodules.

A component is simply a git submodule. The terminology _component_ comes
from `component based architecture` principles, where a component is an
isolated module that is built for reuse.

Git-project is constructed with the assumption that the same components are
reused across multiple projects, probably with different configurations, perhaps
even of different versions, and that the components are distributed using
source code instead of compiled libraries.

### Git Submodule References

* [Git Docs](http://git-scm.com/docs/git-submodule)
* [Git Book](https://git-scm.com/book/en/v2/Git-Tools-Submodules)

## INSTALLATION

### First Time Installation - Debian package

Build a debian package:

$ `make deb`

Install package:

$ sudo `dpkg --install dist/<YOUR-DIST>/*.deb`

It will fail due to missing dependencies and failed configuration.

Run the following to resolve the missing dependencies and failed configuration:

$ sudo `apt-get install`

### First Time Installation

Run:

$ sudo `make install`

To learn about the default installation path or how to change the installation
path, run:

$ `make help`

### Update

Once installed, to get the latest version run:

$ `git project sw-update`

### Check Version

To check which version is installed, run:

$ `git project --version`


## DOCUMENTATION

After installation, the documentation is available as man-pages to
_gitproject-userguide_ (this guide) and _git-project_, the top command.

A short usage description is also available by passing the -h flag to the command.

$ `git project -h`

The man pages can in addition to _man git-project(1)_ also be shown using:

$ `git project --help`

All commands has its own usage description and man pages.

$ `git project <command> -h|--help`

To view the HTML-version of the documentation use:

$ `git project [<command>] --help --web`

$ `git help gitproject-userguide --web`


## BASIC USE

### List Available Commands

To list the available commands, run:

$ `git project --commands`

### Create a Project Repository

To create a new project repository, create a folder just as you would for
a standard git repository, but instead of _git init_, run:

$ `git project init`

If you want to use a different template than the standard template,
pass the path to the template repository using:

$ `git project init --template "<path-to-repo>"`

If the project already has an empty central repository that should be considered its
origin, it can be assigned directly using

$ `git project init --origin "<path-to-repo>"`

### Clone a Project Repository

To clone a project repository and have it automatically do all needed configuration
and download of sub-components, run:

$ `git project clone "<path-to-repo>"`

git project clone supports the same clone arguments as `git clone`.

### Check Project Status

To check the status of the entire project repository, run:

$ `git project status`

### Create a Branch

To create a branch in the project repository and all its components, and have
the submodule track the new branch, run:

$ `git project branch <branch-name>`

To only create the branch in some of the components use:

$ `git project branch <branch-name> "<Component A>" "<Component B>"`

git project branch will automatically checkout the branch created. This since
it does modifications to files in your workspace and to minimize risk of
accidentally committing those changes to the wrong branch.

### Commit

To commit added files in top repository and components, run:

$ `git project commit --message "<message>" ["<Component A>" ....]`

As with many of the git project commands, to only affect some of the
components, list the components to be affected. If no components are specified
all are affected.

git project commit supports most of the options regular `git commit` does.

### Checkout

To checkout a branch and get a working tree, run:

$ `git project checkout <branch-name>`

### Rebase

To rebase your current work, run:

$ `git project rebase <branch-name>`

where branch-name is the name of the branch you want to rebase your work
on-top off.

### Merge

To merge your current work with another branch, run:

$ `git project merge <branch-name> "<commit message>`

where branch-name is the name of the branch you want to merge your
work with.


## WORKFLOW

### Starting a Project

The company/organization have defined a project template that the git-project
configuration points to. To see which template are in use by default, run:

$ `git project init --print-template`

To use a different template than the predefined one, use the --template option, e.g:

$ `git project init --template git@git:mytemplate`

If you already from the start know which repository you want to have as your
remote origin, you can set it as part of the initialization, via:

$ `git project init --origin git@git:myproject`

### Basic Feature Development

**Introduction**

The regular workflow of short-lived topic branches is using:

1. git clone
1. git branch
1. git commit
1. git rebase
1. git merge
1. git push


works almost completely within the git project context.

1. git project clone
1. git project topic begin
1. git project commit
1. git project rebase
1. git project topic end
1. git push


Lets assume you have a project containing two components in the following
structure:

    ./src/componentA ---> componentA repository
    ./tools/compiler ---> compilerA repository

In addition to the external components, you will have project specific content
stored in the top project repository. So the full structure will look something
like this:

    ./src/projApp
    ./src/componentA
    ./tools/compiler
    ./Makefile
    ./README.md

**Cloning**

We are a new developer to the project so we clone the project for the first time:

$ git project clone git@git:myproject

Everything will be setup ready for use. The project agreed-upon hooks will
already be installed and the submodules initialized and updated.

$ git project status

    b9cc31c
    -------
    On branch master
    nothing to commit, working directory clean

    48d512f src/componentA
    ----------------------
    HEAD detached at 48d512f
    nothing to commit, working directory clean

    484b5d2 tools/compiler
    ----------------------
    HEAD detached at 484b5d2
    nothing to commit, working directory clean

**Feature Branching**

Now we start new feature development that we know will affect componentA.

$ git project topic begin "myfeature" src/componentA

The top repository will be branched, so will componentA from the checked
out revision. The branch "topic-myfeature" will also be checked out in
componentA. (All topic branches begin with topic-)

Part of the branching operation, the branch tracking information for componentA
will be updated in the top repository's .gitmodule file to use the newly created
branch.

$ git project status

    b9cc31c
    -------
    On branch topic-myfeature
    Changes not staged for commit:
      (use "git add <file>..." to update what will be committed)
      (use "git checkout -- <file>..." to discard changes in working directory)

        modified:   .gitmodules

    no changes added to commit (use "git add" and/or "git commit -a")

    48d512f src/componentA
    ----------------------
    On branch topic-myfeature
    nothing to commit, working directory clean

    484b5d2 tools/compiler
    ----------------------
    HEAD detached at 484b5d2
    nothing to commit, working directory clean

**Committing**

After making some changes in the top repository and in the component, it is
time to commit those changes. Just as normal git, stage your changes by adding
them to the index to prepare your commit, in both the component and top repository.
Example status after adding:

$ git project status

    b9cc31c
    -------
    On branch topic-myfeature
    Changes to be committed:
      (use "git reset HEAD <file>..." to unstage)

        modified:   .gitmodules
        modified:   src/projApp/app

    Changes not staged for commit:
      (use "git add <file>..." to update what will be committed)
      (use "git checkout -- <file>..." to discard changes in working directory)
      (commit or discard the untracked or modified content in submodules)

        modified:   src/componentA (modified content)


    48d512f src/componentA
    ----------------------
    On branch topic-myfeature
    Changes to be committed:
      (use "git reset HEAD <file>..." to unstage)

        new file:   myfeature.txt


    484b5d2 tools/compiler
    ----------------------
    HEAD detached at 484b5d2
    nothing to commit, working directory clean


git project commit will commit your changes in the correct order and automatically
add affected components to the top repository, so the new revisions in the
submodules becomes part of the top repository commit.

$ git project commit --message "Added my feature"

    src/componentA
    --------------
    [topic-myfeature 363983a] Added my feature
     1 file changed, 0 insertions(+), 0 deletions(-)
     create mode 100644 myfeature.txt

    tools/compiler
    --------------
    Nothing to commit for tools/compiler.

    .
    -
    [topic-myfeature 98af35c] Added my feature
     3 files changed, 3 insertions(+), 1 deletion(-)

The underscored dot represents the commit done in the top repository.

**Rebasing**

When "my feature" is done it is time rebase it back onto the main branch we started from.
If no new commits exist on main then it can be fast-forwarded. git project rebase will
rebase all submodules according to the options specified, and lastly the main project repository.
(make sure that main branches is up to date before rebase)

1. git project checkout "main-branch"
2. git project pull
3. git project topic checkout topic-myfeature


Then it is time to rebase:

$ git project rebase master

    ********  Rebasing module /home/pahus/dev/myproject/src/componentA  master ****
    Current branch topic-myfeature is up to date.
    ********  Rebasing module /home/pahus/dev/myproject  master ********
    Current branch topic-myfeature is up to date.

**Ending a Topic Branch**

After rebasing it is time to merge the topic branch and main branch. topic end will merge the
subrepositories first and then merge the top repository. topic end will update the tracking branch
for all sub repositories to track the upstream branch that is currently checked out and commit those
changes.

Make sure that you first checkout the main repo before with git project checkout "main-branch"

$ git project checkout master

Continue with topic end and give an suitable commit message:

$ git project topic end topic-myfeature "end topic-myfeature"

    Updating 1759ce4..e8fb198
    Fast-forward (no commit created; -m option ignored)
     myfeature.txt | 2 +-
     1 file changed, 1 insertion(+), 1 deletion(-)
    Already up-to-date.
    On branch master
    Your branch is up-to-date with 'origin/master'.

    Changes to be committed:
      (use "git reset HEAD <file>..." to unstage)

            modified:   src/componentA

    Merge made by the 'recursive' strategy.
     .gitmodules     | 2 +-
     src/projApp/app | 2 +-
     2 files changed, 2 insertions(+), 2 deletions(-)

**Push**

Pushing the final main branch is done with ordinary git push and it should be executed in
the submodules first and last in the top repo.

$ git push origin master:master

Or one command that performs everything automatically:

$ git push origin master:master --recurse-submodules =on-demand


### Extended scenarios

**Push local topic to remote topic branch**

Pushing the local topic branch is done with ordinary git push and it should be executed in
the submodules first and last in the top repo

$ git push origin topic-myfeature:topic-myfeature


**topic delete**

After the topic branch is merged back into master the topic branch can be removed in both local and remote
repository by using git project topic delete.

$ git project topic delete topic-myfeature


    Deleting 'topic-myfeature' in 'src/componentA'
    Deleted branch topic-myfeature (was 5c6d0b1).
    To /remote path/componentA.git
     - [deleted]         topic-myfeature
    Deleting 'topic-myfeature' in '.'
    Deleted branch topic-myfeature (was 7abdb73).
    To /remote path/project.git/
     - [deleted]         topic-myfeature


## SANDBOX

If you want to try out (or test) git project with a minimum of hassle, it is possible to
create a tiny sandbox project repository with two submodules on local disc.

$ `make sandbox DEST=<path>`

It will create three bare repositories in &lt;path&gt; named:

* project.git
* product.git
* tools.git

The project.git repository will have product.git and tools.git as subrepositories.

To start using the project repository, clone the project.git repository:

$ git project clone &lt;path&gt;/project.git

Your remote repositories will be the three repositories in &lt;path&gt;.


## THE GITS OF IT ALL

TODO


## CONTRIBUTERS

### Authors

Principle authors of the original project:

* Per Böhlin
* Torbjörn Axelsson
* Magnus Berg
* Jonatan Isaksson
* Patrik Huss

### Other Open Source Projects

Git project uses code and components of other Open Source Projects.

  [Git Extras](https://github.com/tj/git-extras)

  [Git Hooks](https://github.com/icefox/git-hooks)

  [Ronn](https://github.com/rtomayko/ronn)

  [Sharness](https://github.com/mlafeldt/sharness)
