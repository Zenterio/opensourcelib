
.PHONY: clean
clean:  cleanversion
	$(Q)rm -rf $(BUILDDIR)

.PHONY: cleanvm
cleanvm:
	vagrant destroy -f || true

.PHONY: cleanup
cleanup: clean cleandist cleanvm

.PHONY: cleanversion
cleanversion:
	$(Q)rm -f lib/version
