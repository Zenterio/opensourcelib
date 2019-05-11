#
# Simple Makefile for Buildinfo. Archives needed files
#

VERSION=1.0
DIR_NAME=buildinfo
DIST_ARCHIVE=Buildinfo-$(VERSION)

DIST_ARCHIVE:=$(DIST_ARCHIVE).tgz
MKDIR = mkdir

FILES = .python-version \
	*.py \
	*.sh \
	README \
	requirements.txt

dist: $(DIST_ARCHIVE)

$(DIST_ARCHIVE) : $(FILES)
	$(MKDIR) -p $(DIR_NAME)
	cp -r --parents --dereference $(FILES) $(DIR_NAME)
	tar cvzf $(DIST_ARCHIVE) $(DIR_NAME)
	$(RM) -rf $(DIR_NAME)

clean:
	$(RM) $(DIST_ARCHIVE)
