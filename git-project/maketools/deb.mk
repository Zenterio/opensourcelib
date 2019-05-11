
.PHONY: package
package: export DO_TEST=n
package:
	$(Q)$(MAKE) --no-print-directory vagrant_full_systest

.PHONY: deb
deb: $(DEB_FILE)

$(DEB_FILE): export DEB_INSTALL=true
$(DEB_FILE): lib/version debian debian/changelog prepare | $(DEBDIR)
	$(Q)$(DRYRUN) dpkg-buildpackage -i -uc -us -b
	$(Q)$(DRYRUN) mv ../$(PACKAGE_NAME)_*.deb ./$(DEBDIR)
	$(Q)$(DRYRUN) mv ../$(PACKAGE_NAME)_*.changes ./$(DEBDIR)/
	$(Q)$(DRYRUN) lesspipe ./$(DEBDIR)/$(PACKAGE_NAME)_*.deb

debian: $(wildcard debian_config/*)
	$(Q)$(DRYRUN) rm -rf debian
	$(Q)$(DRYRUN) cp -r debian_config debian
	$(Q)$(DRYRUN) rm debian/changelog


.PHONY: vagrant_deb
vagrant_deb: vagrant_deb_u14 vagrant_deb_u16 vagrant_deb_u18

.PHONY: vagrant_deb_u14
vagrant_deb_u14:
	vagrant up u14_deb_builder
	vagrant ssh u14_deb_builder -c "sudo make -C /vagrant deb DO_TEST='$(DO_TEST)' BUILD_NUMBER=${BUILD_NUMBER}"
ifneq ($(strip $(VAGRANT_HALT)),n)
	vagrant halt u14_deb_builder
endif

.PHONY: vagrant_deb_u16
vagrant_deb_u16:
	vagrant up u16_deb_builder
	vagrant ssh u16_deb_builder -c "sudo make -C /vagrant deb DO_TEST='$(DO_TEST)' BUILD_NUMBER=${BUILD_NUMBER}"
ifneq ($(strip $(VAGRANT_HALT)),n)
	vagrant halt u16_deb_builder
endif

.PHONY: vagrant_deb_u18
vagrant_deb_u18:
	vagrant up u18_deb_builder
	vagrant ssh u18_deb_builder -c "sudo make -C /vagrant deb DO_TEST='$(DO_TEST)' BUILD_NUMBER=${BUILD_NUMBER}"
ifneq ($(strip $(VAGRANT_HALT)),n)
	vagrant halt u18_deb_builder
endif

.PHONY: cleandist debclean
cleandist debclean:
	$(Q)$(DRYRUN) rm -rf $(DISTDIR)
	$(Q)$(DRYRUN) rm -rf debian
