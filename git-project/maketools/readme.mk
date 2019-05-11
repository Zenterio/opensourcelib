
.PHONY: readme
readme: $(MANDIR)/gitproject-userguide.7
	$(Q)$(MANTOOL) $(MANDIR)/gitproject-userguide.7

.PHONY: readme-html
readme-html: $(MANDIR)/gitproject-userguide.html
	$(Q)xdg-open $(MANDIR)/gitproject-userguide.html

.PHONY: dev-readme
dev-readme: $(MANDIR)/gitproject-devguide.7
	$(Q)$(MANTOOL) $(MANDIR)/gitproject-devguide.7

.PHONY: dev-readme-html
dev-readme-html: $(MANDIR)/gitproject-devguide.html
	$(Q)xdg-open $(MANDIR)/gitproject-devguide.html
