.PHONY: test
ifneq ($(SYSTEM_TEST),y)
test: prepare
endif
test:
	$(Q)cd $(TESTDIR) && $(MAKE) --no-print-directory test \
		TEST_OPTS="$(TEST_OPTS)" \
		SYSTEM_TEST=$(SYSTEM_TEST)

.PHONY: prove
ifneq ($(SYSTEM_TEST),y)
prove: prepare
endif
prove:
	$(Q)cd $(TESTDIR) && $(MAKE) --no-print-directory prove \
		PROVE_OPTS="$(PROVE_OPTS)" \
		TEST_OPTS="$(TEST_OPTS)" \
		SYSTEM_TEST=$(SYSTEM_TEST)

.PHONY: check
check: clean cleandist test
	$(Q)$(MAKE) --no-print-directory vagrant_full_systest

.PHONY: systest_u14 systest_u16 systest_u18
systest_u14 systest_u16 systest_u18:
	$(Q)$(DRYRUN) testinfra -v /vagrant/systest/install.py /vagrant/systest/systest_*.py /vagrant/systest/uninstall.py \
		--junit-xml /vagrant/$(BUILDDIR)/report_$@.xml

# Due to bad dependencies, we need to build all debian packages before
# running the system tests. This because building a debian package cleans,
# including test reports.
.PHONY: vagrant_full_systest
vagrant_full_systest: vagrant_deb
	$(Q)$(MAKE) --no-print-directory vagrant_u14_systest
	$(Q)$(MAKE) --no-print-directory vagrant_u16_systest
	$(Q)$(MAKE) --no-print-directory vagrant_u18_systest

.PHONY: vagrant_u14_systest
vagrant_u14_systest:
	$(Q)$(DRYRUN) vagrant up u14
	$(Q)$(DRYRUN) vagrant ssh u14 -c "make --no-print-directory -C /vagrant systest_u14"
ifneq ($(strip $(VAGRANT_HALT)),n)
	$(Q)$(DRYRUN) vagrant halt
endif

.PHONY: vagrant_u16_systest
vagrant_u16_systest:
	$(Q)$(DRYRUN) vagrant up u16
	$(Q)$(DRYRUN) vagrant ssh u16 -c "make --no-print-directory -C /vagrant systest_u16"
ifneq ($(strip $(VAGRANT_HALT)),n)
	$(Q)$(DRYRUN) vagrant halt u16
endif

.PHONY: vagrant_u18_systest
vagrant_u18_systest:
	$(Q)$(DRYRUN) vagrant up u18
	$(Q)$(DRYRUN) vagrant ssh u18 -c "make --no-print-directory -C /vagrant systest_u18"
ifneq ($(strip $(VAGRANT_HALT)),n)
	$(Q)$(DRYRUN) vagrant halt u18
endif

.PHONY: before-commit
before-commit:
	$(Q)$(MAKE) --no-print-directory clean
	$(Q)$(MAKE) --no-print-directory docs
	$(Q)$(MAKE) --no-print-directory check
	$(Q)$(MAKE) --no-print-directory prove PROVE_OPTS="-j8"
	$(Q)$(MAKE) --no-print-directory clean
	$(Q)$(MAKE) --no-print-directory docs

.PHONY: test-env
test-env:
	$(Q)cd $(TESTDIR) && $(MAKE) --no-print-directory test \
		TEST_OPTS="-v" TEST_FILTER="lib/env"

.PHONY: testclean
testclean:
	$(Q)cd $(TESTDIR) && $(MAKE) --no-print-directory clean

clean: testclean
