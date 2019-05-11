gitproject-devguide(7) -- Development Guide
========================================================

## INTRODUCTION

This page is for developers of the git-project tool set. As a pure user of
git-project, this page should hold little interest for you.

## INSTALL DEVELOPMENT TOOLS

Run:

$ `make dev-install`

It installs ronn as a user local gem (ruby package). It requires that gem 2 (ruby 2)
is installed. Ronn is used for document generation.

If you are using a system such as Suse that uses a different user for sudo
invocations, please set the path to ronn manually by issuing:

$ `sudo git config --global project.dev.ronn-path PATH-TO-RONN`

or set the path on system level using _--system_.

## GENERATE DOCUMENTATION

The documentation is generated using ronn, installed by `make dev-install`,
which converts markdown files to roff man-pages and HTML files.

To generate the documentation execute:

$ `make docs`

The documentation is generated in the man directory.

After updated the documentation, always generate it and check in the
generated files. File generation should not be part of the installation
process since it might be conflicts in the users environment.

## RUNNING TESTS

Tests can be run in sequence using:

$ `make check [TEST_FILTER="<PATTERN>"] [TEST_OPTS="-h|-v"]`

or use `prove` as the test runner and run in parallel and in random order using:

$ `make prove [TEST_FILTER="<PATTERN>"] [PROVE_OPTS="-j8"] [TEST_OPTS="-h|-v"]`

It is highly recommended that you run make prove with option -jN to execute
tests in parallel. It helps with identifying test dependencies, race-conditions
and other things that indicate a dubious test.

### Dev Test and System Test

By default the test is performed on the current state of development, the files
in the working area.

However, if the variable SYSTEM_TEST is defined, the tests
are run against the current installation. In this mode, not all tests will be
run since some tests modifies the current installation or have under dependencies
that make them unsuitable to run on system level.

### Filter Tests

TEST_FILTER takes GLOB file pattern to match against the test files in the
test directory. The file extension .test is concatenated onto the pattern and
should not be part of the pattern itself.

The filter can be used to select a subset of the tests to be run. By default, all
tests are run (pattern: *).

### Test Groups

The test suites are divided into groups by naming convention of the files:

  * 0000:
    Template, not allowed to have test extension

  * 000X:
    Installation & software update tests

  * NNNX:
    Command NNN, yes we have head-room for more than 99 commands

### Examples

Run all tests in parallel using 8 concurrent process:

$ `make prove PROVE_OPTS="-j8"`

Run all tests for commands 1-4 in sequence:

$ `make check TEST_FILTER="??[1-4]?-*"`

Run single test in verbose mode for trouble-shooting:

$ `make check TEST_FILTER=0030-*" TEST_OPTS="-v"`

Print the test cases that would be run by selected filter:

$ `make check TEST_FILTER="??[1-9]?-*" TEST_OPTS="-h"`


## ARCHITECTURE

git-project makes use of the general sub-command structure of git that
allows any command in the users path that with starts with git-`COMMAND`
to be executed by git.

`git COMMAND --help`, equivalent to `git help COMMAND`, will always
launch the man page `git-COMMAND(1)`.

In addition to performing basic tasks, `git-project` also acts as a dispatcher
to sub-commands. It will dispatch git project `SUBCOMMAND` to `git-project-SUBCOMMAND`.

Each command/subcommand is implemented in its own file. The main implementation
language is bash. The file is placed in the `bin` directory.

All commands/subcommands are documented using markdown. HTML and roff man pages
are generated using ronn as part of the document generation step.
Each command/subcommand has its own documentation file in the `man` directory.

All commands/subcommands have bash completion, implemented in a file named "git_project_[command].sh", located in the
`bash_completion/` folder.

The bash scripts use a library include system where functions are included
using:

    ##lib-name##

All library functions are stored in the `lib` directory. Each file contains a
single function and is named after the function it contains. The install step
performs inlining of all the included libraries before they are copied to the
destination directory. Hence, don't expect to be able to run the commands
directly from the bin directory. The processed version of the command scripts
are temporarily stored in the build directory. To prevent make from deleting
the intermediate files, add the option `KEEP_BUILD_FILES=y` when running make.

Typical work flow:

* Create document file in `man` directory, named `git-project-SUBCOMMAND.mk`,
    using the template man/template.md.

* Create command file in `bin` directory, named `git-project-SUBCOMMAND`,
    no file extension, using the template bin/template.

* Update /etc/bash_completion.sh.

* Test your command extensively!

* Run `make docs` to generate the documentation.

* Check in your changes including the generated documentation.

`!! Make sure to generate all documentation before committing !!`

## CONFIGURATION

All values that are subject to change and can be considered configuration should
not be hard-coded into scripts. Instead they should be written to the system
or user git config under the section `project`.

Installation configuration should be stored in config/.gitproject and read
during the installation using: `git config --file config/.gitproject project.KEY`.

## WRITING DOCUMENTATION

Use the template _man/template.md_ for writing documentation.

Use the following format for single commands:

$ `command options`

Only use level-1 heading on the top heading indicating the command. The format
is Ronn specific.

Use level-2 and level-3 headings to organize your content. Level-2 headings are
written with all capital letters. Level-3 headings follow standard English rules
for capitalization of words in titles.

Text written on level-2 should be left aligned. Exception to this rule is options
bullet list that is indented 2 spaces. Options list should always be written:

    * -short, --long option:
    description of option

Text written on level-3 should be indented two spaces to make it easier
to follow the structure of the document. See README.md as an example.

Larger code examples, console commands and output examples and should be written
with 4 space indentation since that results in no-formatting.

Markdown files should maintain ca 80-100 character width.

## WRITING COMMANDS

Use the template _bin/template_ for writing bash script commands.

The library function replaces all tags ##lib## with the library
definition, found in _lib_.

This mechanism is used to utilize code reuse without being forced to maintain
complex sourcing schemes.

## WRITING TESTS

The test framework used is `sharness`, which is a bash testing framework based
on the framework used to test git.

Test cases should be placed in the test directory, prefix with a test group code,
see [Test groups](#Test-Groups) above, followed by the name of the test suite and
with the _.test_ file extension.

    NNNN-name-of-suite.test

Modifications has been done to the sharness Makefile and sharness.sh to fit the
git-project context. A wrapper file is also used to include additional test-libraries
and extensions.

To write a test, use the 0000-template file in the test directory as template.

Additional information about sharness can be found in tools/sharness,
including the original source code. Sharness is distributed under GPL, and hence
all the modifications to sharness is also covered by GPL.

### System tests

When writing new tests make sure to tag all tests that are not suitable for
system test such as active system update, with DEV_TEST.

    test_expect_sucess DEV_TEST 'my special test' ''

Reversely, tests that are purely system tests should be tagged with SYSTEM_TEST.

## WRITING GUIDES, SECTION-7 MAN PAGES

Guides are placed in files named `gitproject-GUIDE.md`.
They should be marked as being part of section-7 of the man pages.

The naming convention gitproject without dash between git and project,
cause the make file to create a section-7 named man-page file and the installation
procedure to copy the file to man/man7 directory.

## EXTERNAL RESOURCES

This project make use of code from other Open Source projects.
Please respect their copyright and make sure to update the
`contributers` section in README.mk.

## REFERENCES

[How to install ronn manually](https://github.com/rtomayko/ronn/blob/master/INSTALLING)

[How to write markdown](http://daringfireball.net/projects/markdown)

[How to write tests in sharness](https://github.com/mlafeldt/sharness)
