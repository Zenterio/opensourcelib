
.PHONY: debug-print-value-%
debug-print-value-%:
	@echo "$($*)"

.PHONY: debug-print-%
debug-print-%:
	@echo "$*=$($*)"

.PHONY: debug-is-def-%
debug-is-def-%:
ifdef $*
	@true
else
	@false
endif

.PHONY: debug-origin-%
debug-origin-%:
	@echo $(origin $*)

# Development utilities

# Find files with tabs that should not have any,
# this target should give no ouput.
# The find will exit with code 123 if no files are found,
# use || true to ignore that and not get make message about
# ignoring error.
.PHONY: files-with-tabs
files-with-tabs:
	@echo "Files with tabs (empty list is good):"
	$(Q)find . -type f ! -path './.*' ! -path './build/*' ! -path './tools/*' ! -name "Makefile" ! -name "sharness.sh" ! -name "*~" | xargs grep -l -P '\t' || true

.PHONY: sandbox
# Create bare sandbox repositories in DEST/remotes
# make sandbox DEST=<target>
# DEST must be set and DEST/remotes may not exist.
sandbox:
ifndef DEST
	$(error DEST is not set)
endif
	$(Q)tools/create_sandbox.sh "${DEST}"
