# GIT PROJECT
#
# Add DRYRUN=echo to echoing some of the commands instead of performing them.
# It does not always have the intended effect, so use with care and only during
# trouble shooting.
#
# Set KEEP_BUILD_FILES=y to have intermediate bash files not deleted from build
# directory.
#
# Set NO_DELETE_ON_ERROR=y to prevent target files from being deleted on target
# error.
#
# All known variables can be printed
# $ make debug-print-VARNAME
#
# Or just their values
# $ make debug-print-value-VARNAME
#
# and checked if they are defined
# $ make debug-is-def-VARNAME
#
# and their origin printed
# $ make debug-origin-VARNAME
#

include maketools/help.mk

ifndef NO_DELETE_ON_ERROR
.DELETE_ON_ERROR:
endif

include maketools/constants.mk

# Variables
BINS := $(sort $(wildcard $(BINDIR)/git-*[A-Za-z0-9]))
COMMANDS := $(subst $(BINDIR)/,,$(BINS))
BUILT_COMMANDS := $(addprefix $(BUILDDIR)/,$(COMMANDS))
COMPLETIONS := $(wildcard $(COMPLETIONDIR)/git_*.sh)
GUIDES := $(wildcard $(MANDIR)/gitproject*.md)
#Note, gitproject-userguide.md is never created, it is just added here for greating other variables
GUIDES += $(MANDIR)/gitproject-userguide.md
INSTALLS := $(addprefix install.,$(COMMANDS))
INSTALLS += $(addprefix install.,$(notdir $(basename $(GUIDES))))
INSTALLS += install.bash_completion install.config
UNINSTALLS := $(addprefix uninstall.,$(COMMANDS))
UNINSTALLS += $(addprefix uninstall.,$(notdir $(basename $(GUIDES))))
UNINSTALLS += uninstall.bash_completion uninstall.config
MANS := $(wildcard $(MANDIR)/git-*.md)
MAN_PAGES := $(MANS:.md=.1)
MAN_HTMLS := $(MANS:.md=.html)
GUIDE_PAGES := $(GUIDES:.md=.7)
GUIDE_HTMLS :=$(GUIDES:.md=.html)
TOOLS := $(notdir $(filter-out %.install,$(wildcard $(TOOLSDIR)/*[A-Za-z0-9])))
TOOL_INSTALLS := $(addprefix install.tool.,$(notdir $(basename $(wildcard $(TOOLSDIR)/*.install))))

LIBS := $(notdir $(wildcard $(LIBDIR)/*[A-Za-z0-9])) version

Q=@
ifdef VERBOSE
	Q=
endif

# Targets

## Versioning
$(LIBDIR)/version: Makefile
	$(Q)$(DRYRUN) echo "VERSION='$(VERSION_STRING)'" > $(LIBDIR)/version
	$(Q)$(DRYRUN) sync

debian/changelog: debian Makefile
	$(Q)$(DRYRUN) cat debian_config/changelog | sed '1 s/(VERSION)/($(VERSION_STRING))/' > debian/changelog


## Debian packaging
include maketools/deb.mk


## Artifact generation

.PHONY: commands
commands: $(BUILT_COMMANDS)

.PHONY: install
install: $(INSTALLS)
	$(Q)$(DRYRUN) PATH=$(BINDEST):$$PATH git project --version
ifndef KEEP_BUILD_FILES
	$(Q)$(DRYRUN) rm -rf $(BUILDDIR)
endif

.PHONY: uninstall
uninstall: $(UNINSTALLS)

### Prepare artifacts
# Since we are doing concurent testing, and each test case does a
# make install, we need to ensure that everything is pre-generated not to
# have half-finished generated artifacts interfere.
.PHONY: prepare
prepare: docs commands

## Clean
include maketools/clean.mk

## Read me
include maketools/readme.mk

## bash completion

.PHONY: install.bash_completion
install.bash_completion: $(COMPLETIONS) | $(COMPLETIONDEST)
	$(Q)$(DRYRUN) cp -f $(COMPLETIONDIR)/git_*.sh $(COMPLETIONDEST)
	@echo "Installed bash completion"

.PHONY: uninstall.bash_completion
uninstall.bash_completion:
	$(Q)$(DRYRUN) rm -f $(COMPLETIONDEST)/git_project*.sh
	$(Q)$(DRYRUN) rm -f $(COMPLETIONDEST)/git_buildinfo*.sh
	@echo "Uninstalled bash completion"


## git-project config
include maketools/config.mk


## dev install
.PHONY: dev-install
dev-install: $(TOOL_INSTALLS)

.PHONY: dev-uninstall
dev-uninstall:
	$(Q)git config --global --remove-section project.dev > /dev/null 2>&1 || true
	@echo "Please remove the tools installed manually:"
	@echo "$(notdir $(basename $(wildcard $(TOOLSDIR)/*.install)))"

## lint
include maketools/lint.mk

## test
include maketools/test.mk

## documentation
include maketools/docs.mk

## Directories
$(BUILDDIR) $(BINDEST) $(MANDEST1) $(MANDEST7) $(COMPLETIONDEST) $(GITDOCDEST) $(DISTDIR) $(DEBDIR):
	$(Q)mkdir -p "$@"


# Rules

## Artifact creation

### Generate bash script with library expanded/included
$(BUILDDIR)/git-%: $(BINDIR)/git-% $(addprefix $(LIBDIR)/, $(LIBS))| $(BUILDDIR)
	$(Q)cp -f $< $@
	$(Q)$(foreach lib,$(LIBS),sed -i -e "/^\#\#$(lib)\#\#/r $(LIBDIR)/$(lib)" -e "/^\#\#$(lib)\#\#/d" $@;)
	$(Q)! grep '^##.*##' "$@"
	$(Q)sync

## Install rules

### Commands
.PHONY: install.git-%
install.git-%: git-%.command.install git-%.1.install git-%.html.install
	@echo "installed git-$*"

### Guides
.PHONY: install.gitproject-%
install.gitproject-%: gitproject-%.7.install gitproject-%.html.install
	@echo "installed guide $* (gitproject-$*)"

### Default
.PHONY: install.%
install.%: %.1.install %.html.install
	@echo "Installed $*"

.PHONY: git-%.command.install
git-%.command.install: $(BUILDDIR)/git-% | $(BINDEST)
	$(Q)$(DRYRUN) cp -f $< $(BINDEST)/$(notdir $<)

.PHONY: git%.1.install
git%.1.install: | $(MANDEST1)
	$(Q)$(DRYRUN) cp -f $(MANDIR)/git$*.1 $(MANDEST1)/git$*.1

.PHONY: git%.7.install
git%.7.install: | $(MANDEST7)
	$(Q)$(DRYRUN) cp -f $(MANDIR)/git$*.7 $(MANDEST7)/git$*.7

.PHONY: git%.html.install
git%.html.install: html-dest-setup
	$(Q)$(DRYRUN) cp -f $(MANDIR)/git$*.html $(GITDOCDEST)/git$*.html


## Uninstall rules

### Commands
.PHONY: uninstall.git-%
uninstall.git-%: git-%.command.uninstall git-%.1.uninstall git-%.html.uninstall
	@echo "uninstalled git-$*"

### Guides
.PHONY: uninstall.gitproject-%
uninstall.gitproject-%: gitproject-%.7.uninstall gitproject-%.html.uninstall
	@echo "uninstalled guide $* (gitproject-$*)"

### Default
.PHONY: uninstall.%
uninstall.%: %.1.uninstall %.html.uninstall
	@echo "uninstalled $*"

.PHONY: git-%.command.uninstall
git-%.command.uninstall:
	$(Q)$(DRYRUN) rm -f $(BINDEST)/git-$*

.PHONY: git%.1.uninstall
git%.1.uninstall:
	$(Q)$(DRYRUN) rm -f $(MANDEST1)/git$*.1

.PHONY: git%.7.uninstall
git%.7.uninstall:
	$(Q)$(DRYRUN) rm -f $(MANDEST7)/git$*.7

.PHONY: git%.html.uninstall
git%.html.uninstall:
	$(Q)$(DRYRUN) rm -f $(HTMLDEST)/git$*.html


## Install tools

.PHONY: install.tool.%
install.tool.%: $(TOOLSDIR)/%.install
	@echo "Installing tool $*"
	$(Q)$(DRYRUN) $<


# Debug targets
include maketools/debug.mk
