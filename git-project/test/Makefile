# Run tests
#
# Copyright (c) 2011-2012 Mathias Lafeldt
# Copyright (c) 2005-2012 Git project
# Copyright (c) 2005-2012 Junio C Hamano
# Copyright (c) 2015-     Per Böhlin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/ .
SHELL=/bin/bash
SHELL_PATH ?= $(SHELL)
SHELL_PATH_SQ = $(subst ','\'',$(SHELL_PATH))
RM ?= rm -f
PROVE ?= prove
AGGREGATE_SCRIPT ?= lib/aggregate-results.sh
DEFAULT_TEST_TARGET ?= test
SHARNESS_TEST_EXTENSION ?= test
TEST_FILTER ?= *
TEMP_ROOT = /dev/shm
LINT_TOOL := ../tools/shellcheck/shellcheck
LINT_TOOL_ARGS := --external-sources --exclude=SC2016 --shell=bash -f tty

TEST_FILES := $(sort $(wildcard $(TEST_FILTER).$(SHARNESS_TEST_EXTENSION)))
T := $(addprefix test.,$(subst .$(SHARNESS_TEST_EXTENSION),,$(TEST_FILES)))
LINT_TEST_FILES := $(addprefix lint.,$(subst .$(SHARNESS_TEST_EXTENSION),,$(TEST_FILES)))

all: $(DEFAULT_TEST_TARGET)

test: pre-clean
	@$(MAKE) --no-print-directory aggregate-results-and-cleanup

prove: pre-clean
	@echo "*** prove ***"; \
	SHARNESS_TEST_EXTENSION=$(SHARNESS_TEST_EXTENSION) $(PROVE) \
		--exec '$(SHELL_PATH_SQ)' $(PROVE_OPTS) $(T) :: $(TEST_OPTS)
	@SHARNESS_TEST_EXTENSION=$(SHARNESS_TEST_EXTENSION) \
		$(MAKE) --no-print-directory clean-except-prove-cache

test.%: %.$(SHARNESS_TEST_EXTENSION)
	-INSTALL_ROOT="$(TEMP_ROOT)" SHARNESS_TEST_EXTENSION=$(SHARNESS_TEST_EXTENSION) '$(SHELL_PATH_SQ)' $< $(TEST_OPTS) --root="$(TEMP_ROOT)"

lint: $(LINT_TEST_FILES)

lint.%: %.$(SHARNESS_TEST_EXTENSION)
	@bash -n $<
	@$(LINT_TOOL) $(LINT_TOOL_ARGS) $<

pre-clean:
	@$(RM) -r test-results
	@$(RM) -r install
	@$(RM) -r $(TEMP_ROOT)/sut-*

clean-except-prove-cache: pre-clean
	@$(RM) -r $(TEST_ROOT)/'trash directory'.*

clean: clean-except-prove-cache
	@$(RM) .prove

aggregate-results-and-cleanup: $(T)
	@$(MAKE) --no-print-directory aggregate-results
	@$(MAKE) --no-print-directory clean

aggregate-results:
	@if test ! -d test-results; then true; else \
	for f in test-results/*.counts; do \
		echo "$$f"; \
	done | '$(SHELL_PATH_SQ)' '$(AGGREGATE_SCRIPT)' ; fi

.PHONY: all test prove pre-clean clean
.PHONY: aggregate-results-and-cleanup aggregate-results
