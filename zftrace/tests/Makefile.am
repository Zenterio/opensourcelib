# Automake input for zftrace tests.

TESTS = test_zftrace_version \
		test_zftrace_help \
		test_zftrace_run_default \
		test_zftrace_run_checksum \
		test_zftrace_run_proc \
		test_zftrace_run_checksum_proc \
		test_zftrace_run_kill \
		test_zftrace_link_creation_detection \
		test_zftrace_ignored_report \
		test_zftrace_list_tracked_ignored_files \
		test_zftrace-ln_all \
		test_zftrace-filter_all
		

EXTRA_DIST = init.sh $(TESTS) data scripts

CLEANFILES = check.log

clean-local: clean-local-check

.PHONY:	clean-local-check
clean-local-check:
	rm -rf output
