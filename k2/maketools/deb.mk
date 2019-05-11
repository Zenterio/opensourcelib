

DEB_DEPENDENCIES := k2/version.py $(PY_SOURCES) requirements.txt requirements-dev.txt setup.py $(wildcard debian_config/*)


# Generates targets for building debian packages
#
# $(1) - Name of the node
define BUILD_DEB

$(1)_DEB := zenterio-zk2_$(VERSION_STRING)+$(NODE_$(1)_CODENAME)_amd64.deb
$(1)_DIST := dist/$(NODE_$(1)_CODENAME)/$$($(1)_DEB)

$$($(1)_DIST): SHELL := $$(NODE_$(1)_SHELL)
$$($(1)_DIST): .SHELLFLAGS := $$(NODE_$(1)_SHELLFLAGS)
$$($(1)_DIST): BASH_ENV :=
$$($(1)_DIST): ./docker/markers/docker_node_$(1)_built.marker $$(DEB_DEPENDENCIES) $$(DOCS)
	cp -r debian_config/. debian/; \
	mkdir -p debian/doc/user_guide/pdf; \
	mkdir -p debian/doc/dev_guide/pdf; \
	cp doc/build/user_guide/pdf/user_guide.pdf debian/doc/user_guide/pdf; \
	cp doc/build/dev_guide/pdf/dev_guide.pdf debian/doc/dev_guide/pdf; \
	cp -r doc/build/user_guide/html debian/doc/user_guide/; \
	cp -r doc/build/dev_guide/html debian/doc/dev_guide/; \
	sed -i '1 s/(VERSION)/($$(VERSION_STRING)+$$(NODE_$(1)_CODENAME))/' debian/changelog; \
	dpkg-buildpackage -us -uc; \
	mkdir -p ./dist/$$(NODE_$(1)_CODENAME); \
	mv -f ../$$($(1)_DEB) $$($(1)_DIST)

deb_$(1): $$($(1)_DIST)
deb: $$($(1)_DIST)

endef

$(eval $(foreach __node,$(DOCKER_BUILD_NODES),$(call BUILD_DEB,$(__node))))
