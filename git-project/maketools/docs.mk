
HTML_PACKAGE := dist/git-project-docs.tar.gz

.PHONY: html-package
html-package: $(HTML_PACKAGE)

package: html-package

$(HTML_PACKAGE): | dist
	$(Q)rm -rf /dev/shm/git-project-docs
	$(Q)mkdir -p /dev/shm/git-project-docs
	$(Q)cp man/git*.html /dev/shm/git-project-docs
	$(Q)rm -f $@
	$(Q)tar -zcf $@ -C /dev/shm/ git-project-docs


.PHONY: docs
docs: $(MAN_PAGES) $(MAN_HTMLS) $(GUIDE_PAGES) $(GUIDE_HTMLS)

.PHONY: docclean
docclean:
	$(Q)rm -f $(MANDIR)/*.1
	$(Q)rm -f $(MANDIR)/*.7
	$(Q)rm -f $(MANDIR)/*.html
	$(Q)rm -f $(HTML_PACKAGE)

clean: docclean



.PHONY: html-dest-setup
html-dest-setup: | $(GITDOCDEST)
ifndef DEB_INSTALL
	$(Q)if [ -h $(HTMLDEST) ]; then \
			:; \
		elif [ -d $(HTMLDEST) ]; then \
			mv $(HTMLDEST)/* $(HTMLDEST)/.[!.]* $(GITDOCDEST); \
			rmdir $(HTMLDEST); \
			ln -s $(GITDOCDEST) $(HTMLDEST); \
		else \
			mkdir -p `dirname $(HTMLDEST)`; \
			ln -s $(GITDOCDEST) $(HTMLDEST);\
		fi
endif

### Project command documentation

$(MANDIR)/git-project%.1: $(MANDIR)/git-project%.md $(MANDIR)/footer.md
	$(Q)cat $^ | $(TOOLSDIR)/ronn \
		--manual "Git Project" \
		--roff \
		--pipe > $@

$(MANDIR)/git-project%.html: $(MANDIR)/git-project%.md $(MANDIR)/hr.md $(MANDIR)/footer.md
	$(Q)cat $^ | $(TOOLSDIR)/ronn \
		--manual "Git Project" \
		--html --style=toc \
		--pipe > $@

### Project guides

$(MANDIR)/gitproject-%.7: $(MANDIR)/gitproject-%.md $(MANDIR)/footer.md
	$(Q)cat $^ | $(TOOLSDIR)/ronn \
		--manual "Git Project" \
		--roff \
		--pipe > $@

$(MANDIR)/gitproject-%.html: $(MANDIR)/gitproject-%.md $(MANDIR)/hr.md $(MANDIR)/footer.md
	$(Q)cat $^ | $(TOOLSDIR)/ronn \
		--manual "Git Project" \
		--html --style=toc \
		--pipe > $@

### git-project user guide (generated from README.md)
$(MANDIR)/gitproject-userguide.7: $(MANDIR)/readme-header.md $(MANDIR)/readme-toc.md README.md $(MANDIR)/footer.md
	@cat $^ |$(TOOLSDIR)/ronn --roff --manual "Git Project User Guide" --pipe > $@

$(MANDIR)/gitproject-userguide.html: $(MANDIR)/readme-header.md README.md $(MANDIR)/hr.md $(MANDIR)/footer.md
	@cat $^ |$(TOOLSDIR)/ronn --html --manual "Git Project User Guide" --style=toc --pipe > $@

### Non-project command documentation, should not have project footer

$(MANDIR)/git-%.1: $(MANDIR)/git-%.md
	$(Q)cat $^ | $(TOOLSDIR)/ronn \
		--manual "Git $*" \
		--roff \
		--pipe > $@

$(MANDIR)/git-%.html: $(MANDIR)/git-%.md
	$(Q)cat $^ | $(TOOLSDIR)/ronn \
		--manual "Git $*" \
		--html --style=toc \
		--pipe > $@
