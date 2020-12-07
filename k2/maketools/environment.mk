DOCKER_REGISTRY := quay.io
image_14 := zenterio/pythontest.u14
image_16 := zenterio/pythontest.u16
image_18 := zenterio/pythontest.u18
image_14_deb_builder := zenterio/debbuilder.u14
image_16_deb_builder := zenterio/debbuilder.u16
image_18_deb_builder := zenterio/debbuilder.u18
image_manylinux_wheel_builder := pypa/manylinux1_x86_64
image_local := dummy

# Defines targets required to create a node.
#
# A node is some target that can be used to run shell commands, for example the
# local host system or a Docker container.
#
# $(1) - Name of the node
# $(2) - Path to the executable used to build the node
# $(3) - Path to the executable used to execute commands on the node
define NODE

NODE_$(1)_SHELL := $(3)
NODE_$(1)_SHELLFLAGS := $(DOCKER_REGISTRY)/$(image_$(1)) latest

./docker/markers/docker_node_$(1)_built.marker: SHELL := $(2)
./docker/markers/docker_node_$(1)_built.marker: .SHELLFLAGS := $(DOCKER_REGISTRY)/$(image_$(1)) latest $(image_$(1))
./docker/markers/docker_node_$(1)_built.marker: $(wildcard docker/Dockerfile.$(1))
	@./docker/markers/docker_node_$(1)_built.marker

build_nodes: ./docker/markers/docker_node_$(1)_built.marker

cleannode_$(1):
	rm -f ./docker/markers/docker_node_$(1)_built.marker

cleannodes: cleannode_$(1)

endef


# Defines targets required to prepare a node for use.
#
# $(1) - Name of the node
define TEST_NODE

./docker/markers/docker_node_$(1)_venv.marker: SHELL := $$(NODE_$(1)_SHELL)
./docker/markers/docker_node_$(1)_venv.marker: .SHELLFLAGS := $$(NODE_$(1)_SHELLFLAGS)
./docker/markers/docker_node_$(1)_venv.marker: ./docker/markers/docker_node_$(1)_built.marker requirements.txt requirements-dev.txt setup.py addons/*/setup.py
	rm -rf .venv/*
	${PYTHON} -m venv .venv
	cp pip.conf .venv/
	.venv/bin/${PYTHON} .venv/bin/pip install --upgrade setuptools
	.venv/bin/${PYTHON} .venv/bin/pip install --upgrade --force-reinstall pip
	cp pip.conf .venv/pip.conf
	cat requirements.txt requirements-dev.txt | grep -v trusted-host | grep -v addons | xargs -L1 -P1 .venv/bin/${PYTHON} .venv/bin/pip install
	cat requirements.txt requirements-dev.txt | grep -v trusted-host | grep addons | xargs -L1 -P1 .venv/bin/${PYTHON} .venv/bin/pip install -e
	.venv/bin/${PYTHON} .venv/bin/pip install -e .
	touch $$@

prepare_node_$(1): ./docker/markers/docker_node_$(1)_venv.marker
prepare_nodes: prepare_node_$(1)


cleanvenv_$(1): SHELL := $$(NODE_$(1)_SHELL)
cleanvenv_$(1): .SHELLFLAGS := $$(NODE_$(1)_SHELLFLAGS)
cleanvenv_$(1):
	rm -rf .venv/*
	rm -rf *.egg-info/
	rm -rf addons/*/*.egg-info/
	rm -f ./docker/markers/docker_node_$(1)_venv.marker

ifeq ($(1),local)
cleanvenv: cleanvenv_$(1)
else ifeq ($(DOCKER_REGISTRY)/$(1),$(shell $(DOCKER_IMAGE) ls --filter 'reference=$(DOCKER_REGISTRY)/$(1)' --format '{{.Repository}}:{{.Tag}}' 2>&1; echo $$?))
cleanvenv: cleanvenv_$(1)
endif
endef

# Defines targets for debugging docker builds by being able to start a shell in a container
#
# $(1) - Name of node
define DOCKER_DEBUG

docker_debug_$(1): ./docker/markers/docker_node_$(1)_built.marker
	maketools/docker/debug.sh $(DOCKER_REGISTRY)/$(image_$(1)) latest

endef


# The BASH_ENV variable tells bash where to find its rc file. If the rc file
# exists, it is sourced by bash on startup.
#
# Lets use this feature to automatically activate the virtual environment.
BASH_ENV := .venv/bin/activate
export BASH_ENV


LOCAL_BUILD := ./maketools/local/build.sh
LOCAL_RUN := ./maketools/local/run.sh
LOCAL_TEST_NODES := local

DOCKER_BUILD ?= ./maketools/docker/build.sh
DOCKER_RUN ?= ./maketools/docker/run.sh
DOCKER_IMAGE ?= ./maketools/docker/image.sh
DOCKER_BUILD_NODES := 14_deb_builder 16_deb_builder 18_deb_builder
DOCKER_WHEEL_BUILD_NODES := manylinux_wheel_builder
DOCKER_TEST_NODES := 14 16 18
DOCKER_NODES = $(DOCKER_BUILD_NODES) $(DOCKER_WHEEL_BUILD_NODES) $(DOCKER_TEST_NODES)

TEST_NODES := $(LOCAL_TEST_NODES) $(DOCKER_TEST_NODES)

NODE_14_CODENAME := trusty
NODE_14_deb_builder_CODENAME := trusty

NODE_16_CODENAME := xenial
NODE_16_deb_builder_CODENAME := xenial

NODE_18_CODENAME := bionic
NODE_18_deb_builder_CODENAME := bionic


$(eval $(foreach __node,$(LOCAL_TEST_NODES),$(call NODE,$(__node),$(LOCAL_BUILD),$(LOCAL_RUN))))
$(eval $(foreach __node,$(LOCAL_TEST_NODES),$(call TEST_NODE,$(__node))))

$(eval $(foreach __node,$(DOCKER_BUILD_NODES),$(call NODE,$(__node),$(DOCKER_BUILD),$(DOCKER_RUN))))
$(eval $(foreach __node,$(DOCKER_WHEEL_BUILD_NODES),$(call NODE,$(__node),$(DOCKER_BUILD),$(DOCKER_RUN))))
$(eval $(foreach __node,$(DOCKER_TEST_NODES),$(call NODE,$(__node),$(DOCKER_BUILD),$(DOCKER_RUN))))
$(eval $(foreach __node,$(DOCKER_TEST_NODES),$(call TEST_NODE,$(__node))))
$(eval $(foreach __node,$(DOCKER_NODES), $(call DOCKER_DEBUG,$(__node))))
