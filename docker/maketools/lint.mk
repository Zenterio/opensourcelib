PWD := $(shell pwd)
LINT := docker run --mount source="${PWD}",target="${PWD}",type=bind --rm -i docker.zenterio.lan/hadolint/hadolint:v1.10.4 hadolint
LINT_IGNORE += DL3006 DL3008 DL3009 DL3013 DL3015 DL4001 DL3007 DL3018

#
# $1 name of image
define LINT_DOCKERFILE

lint_$(1): $(call DOCKER_FILE,$(1))
	$(LINT) $(foreach __ignore,$(LINT_IGNORE),--ignore $(__ignore)) "${PWD}"/$(call DOCKER_FILE,$(1))

check_$(1): lint_$(1)

lint: lint_$(1)

endef

$(eval $(foreach __dockerimage,$(DOCKER_IMAGES),$(call LINT_DOCKERFILE,$(__dockerimage))$(NEW_LINE)))


lint: lint_shellscripts
lint_shellscripts:
	find . -name '*.sh' | xargs -L1 zshellcheck

static: lint
