LINT_COMMANDS := $(addprefix lint.command.,$(COMMANDS))
LINT_FORMAT ?= tty
LINT_TOOL := tools/shellcheck/shellcheck
LINT_TOOL_ARGS := --external-sources --exclude=SC2016 --shell=bash -f $(LINT_FORMAT)

.PHONY: static lint lint-commands lint-test lint-tool-version lint-tool-help

static lint: lint-commands lint-test

lint-commands: $(LINT_COMMANDS)

lint-test:
	$(Q)$(MAKE) --no-print-directory -C$(TESTDIR) lint

lint.command.%: $(BUILDDIR)/%
	$(Q)bash -n $<
	$(Q)$(LINT_TOOL) $(LINT_TOOL_ARGS) $<

lint-tool-version:
	$(Q)$(LINT_TOOL) --version

lint-tool-help:
	$(Q)$(LINT_TOOL) --help
