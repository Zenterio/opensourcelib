# Constants
MANDIR := man
BINDIR := bin
TOOLSDIR := tools
LIBDIR := lib
COMPLETIONDIR := bash_completion
BUILDDIR := build
TESTDIR := test
DISTDIR := dist

VERSION_NUMBER := 0.9.1
CODENAME := $(shell lsb_release -c -s)
DEBDIR := $(DISTDIR)/$(CODENAME)
PACKAGE_NAME := zenterio-git-project

DO_TEST ?= y
HALT_VAGRANT ?= y

ifndef BUILD_NUMBER
	BUILD_NUMBER := 0
endif

ifdef BUILD_UPGRADE_DEB
	DEBDIR := dist/${CODENAME}/upgrade
	VERSION_STRING := ${VERSION_NUMBER}+${BUILD_NUMBER}1+${CODENAME}
else
	VERSION_STRING := ${VERSION_NUMBER}+${BUILD_NUMBER}+${CODENAME}
endif

DEB_FILE := $(DEBDIR)/$(PACKAGE_NAME)_$(VERSION_STRING)_amd64.deb

# Unoffical Optionals
MANTOOL ?= man
DRYRUN ?=
GITCONFIG ?=--system

# Optionals saved in config
ifdef FROM_CONFIG
	DESTDIR ?= $(shell git config $(GITCONFIG) project.install.destdir)
	PREFIX ?= $(shell git config $(GITCONFIG) project.install.prefix)
	HTMLPREFIX ?= $(shell git config $(GITCONFIG) project.install.htmlprefix)
	GITDOCS ?= $(shell git config $(GITCONFIG) project.install.git-doc)
	COMPLETIONPREFIX ?= $(shell git config $(GITCONFIG) project.install.completionprefix)
else
	DESTDIR ?=
	PREFIX ?= /usr
	HTMLPREFIX ?= $(shell git --html-path)
	GITDOCS ?= $(shell git config -f config/.gitproject project.git-doc-path)
	COMPLETIONPREFIX ?= /etc/bash_completion.d
endif

# Destination directories
BINDEST := $(DESTDIR)$(PREFIX)/bin
MANDEST := $(DESTDIR)$(PREFIX)/share/man
MANDEST1 := $(MANDEST)/man1
MANDEST7 := $(MANDEST)/man7
HTMLDEST := $(DESTDIR)$(HTMLPREFIX)
GITDOCDEST := $(DESTDIR)$(GITDOCS)
COMPLETIONDEST := $(DESTDIR)$(COMPLETIONPREFIX)
