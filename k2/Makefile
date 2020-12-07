VERSION_NUMBER := 1.1.0

ifndef BUILD_NUMBER
	BUILD_NUMBER := 0
endif

VERSION_STRING := ${VERSION_NUMBER}+${BUILD_NUMBER}

PYTHON := python3

PY_SOURCES := $(shell find k2 -type f -name '*.py')
PY_SOURCES += $(shell find addons -type f -name '*.py')
RST_SOURCES := $(shell find k2 -type f -name '*.rst')
RST_SOURCES += $(shell find addons -type f -name '*.rst')
FORMAT_SOURCES := $(shell find k2 addons systest -name '*.py' -not -path '*syntaxerror*' -not -path '*generated*' -not -path '*__pycache__*')

ifeq ($(findstring vagrant, $(shell hostname)), )
OUTPUT_DIR=output
else
OUTPUT_DIR=/vagrant/output_$(shell hostname)/
endif

##################################################################
##################################################################

include maketools/environment.mk
include maketools/help.mk
include maketools/pypi.mk
include maketools/doc.mk
include maketools/deb.mk
include maketools/test.mk
include maketools/version.mk

test: test_local
systest: systest_local
static: static_local
benchmark: benchmark_local

.PHONY: check
check: SHELL := $(NODE_local_SHELL)
check: .SHELLFLAGS := $(NODE_local_SHELLFLAGS)
check: static test systest
ifeq ($(filter $(COVERAGE),y),y)
	@echo
	@echo Combined coverage for unit and system tests
	@cp .coverage-local .coverage-local-copy
	@cp .coverage-systest-local .coverage-systest-local-copy
	COVERAGE_FILE=.coverage-all coverage combine .coverage-local-copy .coverage-systest-local-copy
	COVERAGE_FILE=.coverage-all coverage report -m --rcfile=.coveragerc
  ifeq ($(filter $(COVERAGE_XML_REPORT),y),y)
	COVERAGE_FILE=.coverage-all coverage xml -o coverage-all.xml --rcfile=.coveragerc
  endif
endif

.PHONY: package
package: check doc debtest

venv: prepare_node_local

.PHONY: format
format: prepare_node_local
	@.venv/bin/yapf -p --style .yapf --in-place --parallel $(FORMAT_SOURCES)
	@.venv/bin/isort -j8 --multi-line 2 --apply --dont-skip '__init__.py' --line-width 100 --thirdparty zaf $(FORMAT_SOURCES)

.PHONY: clean
clean: cleandoc cleancov clean_systest clean_pypi
	rm -f ../zenterio-zk2*
	rm -rf debian/
	rm -rf dist/
	rm -f k2/version.py
	rm -f .benchmark

.PHONY: cleanup
cleanup: clean cleanvenv cleannodes cleanup_pypi
