

#$1 image name
define IMAGE_FILES

$(1).make_dirs := $(strip $(dir $(shell find images/$(1) -type f -name 'Makefile')))
$(1).znake_dirs := $(strip $(dir $(shell find images/$(1) -type f -name 'znake.yaml')))

endef

# Create static and format targets for images
#
# $1 image name
define STATIC_AND_FORMAT_IMAGE

static: static_$(1)
static_$(1):
ifneq ($($(1).znake_dirs),)
	set -e; $(foreach __dir,$($(1).znake_dirs),cd $(__dir) && znake static; )
endif
ifneq ($($(1).make_dirs),)
	set -e; $(foreach __dir,$($(1).make_dirs),cd $(__dir) && make static; )
endif

format: format_$(1)
format_$(1):
ifneq ($($(1).znake_dirs),)
	set -e; $(foreach __dir,$($(1).znake_dirs),cd $(__dir) && znake format; )
endif
ifneq ($($(1).make_dirs),)
	set -e; $(foreach __dir,$($(1).make_dirs),cd $(__dir) && make format; )
endif

endef

# Create test targets for images
#
# $1 image name
define TEST_IMAGE

test: test_$(1)
test_$(1):
ifneq ($($(1).znake_dirs),)
	set -e; $(foreach __dir,$($(1).znake_dirs),cd $(__dir) && znake test; )
endif
ifneq ($($(1).make_dirs),)
	set -e; $(foreach __dir,$($(1).make_dirs),cd $(__dir) && make test; )
endif

endef

# Create systest targets for images
#
# $1 image name
define SYSTEST_IMAGE

systest: systest_$(1)
systest_$(1):
ifneq ($($(1).znake_dirs),)
	set -e; $(foreach __dir,$($(1).znake_dirs),cd $(__dir) && znake systest; )
endif
ifneq ($($(1).make_dirs),)
	set -e; $(foreach __dir,$($(1).make_dirs),cd $(__dir) && make systest; )
endif

endef

# Create check targets for images
#
# $1 image name
define CHECK_IMAGE

check: check_$(1)
check_$(1):
ifneq ($($(1).znake_dirs),)
	set -e; $(foreach __dir,$($(1).znake_dirs),cd $(__dir) && znake check; )
endif
ifneq ($($(1).make_dirs),)
	set -e; $(foreach __dir,$($(1).make_dirs),cd $(__dir) && make check; )
endif

endef


$(eval $(foreach __dockerimage,$(DOCKER_IMAGES),$(call IMAGE_FILES,$(__dockerimage))$(NEW_LINE)))
$(eval $(foreach __dockerimage,$(DOCKER_IMAGES),$(call STATIC_AND_FORMAT_IMAGE,$(__dockerimage))$(NEW_LINE)))
$(eval $(foreach __dockerimage,$(DOCKER_IMAGES),$(call TEST_IMAGE,$(__dockerimage))$(NEW_LINE)))
$(eval $(foreach __dockerimage,$(DOCKER_IMAGES),$(call SYSTEST_IMAGE,$(__dockerimage))$(NEW_LINE)))
$(eval $(foreach __dockerimage,$(DOCKER_IMAGES),$(call CHECK_IMAGE,$(__dockerimage))$(NEW_LINE)))
