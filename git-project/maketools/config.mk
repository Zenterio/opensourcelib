
.PHONY: $(BUILDDIR)/install.config
$(BUILDDIR)/install.config: | $(BUILDDIR)
	$(Q)$(DRYRUN) echo "#!/usr/bin/env bash" > $@
	$(Q)$(DRYRUN) echo "set -e" > $@
	$(Q)$(DRYRUN) echo "git config $(GITCONFIG) project.update-repo $$(git config --file config/.gitproject project.update-repo)" >> $@
	$(Q)$(DRYRUN) echo "git config $(GITCONFIG) project.template $$(git config --file config/.gitproject project.template)" >> $@
	$(Q)$(DRYRUN) echo "git config $(GITCONFIG) project.install.destdir \"$(DESTDIR)\"" >> $@
	$(Q)$(DRYRUN) echo "git config $(GITCONFIG) project.install.prefix \"$(PREFIX)\"" >> $@
	$(Q)$(DRYRUN) echo "git config $(GITCONFIG) project.install.htmlprefix \"$(HTMLPREFIX)\"" >> $@
	$(Q)$(DRYRUN) echo "git config $(GITCONFIG) project.install.git-doc \"$(GITDOCS)\"" >> $@
	$(Q)$(DRYRUN) echo "git config $(GITCONFIG) project.install.completionprefix \"$(COMPLETIONPREFIX)\"" >> $@
	$(Q)$(DRYRUN) echo "git config $(GITCONFIG) project.install.bin \"$(BINDEST)\"" >> $@
	$(Q)$(DRYRUN) echo "git config $(GITCONFIG) project.install.man \"$(MANDEST)\"" >> $@
	$(Q)$(DRYRUN) echo "git config $(GITCONFIG) project.install.html \"$(HTMLDEST)\"" >> $@
	$(Q)$(DRYRUN) echo "git config $(GITCONFIG) project.install.completion \"$(COMPLETIONDEST)\"" >> $@
ifdef DEB_INSTALL
	$(Q)$(DRYRUN) echo "git config $(GITCONFIG) project.install.method deb" >> $@
else
	$(Q)$(DRYRUN) echo "git config $(GITCONFIG) project.install.method make" >> $@
endif
	$(Q)$(DRYRUN) chmod a+x $@


.PHONY: install.config
install.config: $(BUILDDIR)/install.config
	$(Q)$(DRYRUN)
ifdef DEB_INSTALL
	$(Q)$(DRYRUN) cp $< debian/postinst
else
	$(Q)$(DRYRUN) $<
endif
	@echo "Installed configuration"

.PHONY: uninstall.config
uninstall.config:
	$(Q)$(DRYRUN) git config $(GITCONFIG) --remove-section project > /dev/null 2>&1 || true
	$(Q)$(DRYRUN) git config $(GITCONFIG) --remove-section project.install > /dev/null 2>&1 || true
	@echo "Uninstalled configuration"
