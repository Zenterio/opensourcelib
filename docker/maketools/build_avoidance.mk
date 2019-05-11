BUILD_AVOIDANCE := n

# Creates a target for build avoidance for an image.
#
# The avoid target will be run in dependency order for all images.
# For each image a git diff towards the LAST_SUCCESSFUL_BUILD tag will be
# performed and if the diff doesn't contain any files belonging to the image
# then the build marker file will be touched.
# This will indicate to the 'make image' target that there is no need to build this image.
#
# All output from this target will be treated as an error.
#
# $1 name of image
define CREATE_AVOID

avoid_$(1): $(call IMAGE_PARENT_WITH_PREFIX,$(1),avoid_) | $(BUILD_DIR)
	@git diff --name-only LAST_SUCCESSFUL_BUILD | grep images/$(1) 2>&1 > /dev/null || touch $(BUILD_DIR)/$(1).marker 2>&1

build_avoidance: avoid_$(1)

endef

$(eval $(foreach __dockerimage,$(DOCKER_IMAGES),$(call CREATE_AVOID,$(__dockerimage))$(NEW_LINE)))


ifeq ($(BUILD_AVOIDANCE),y)
  $(info Running build avoidance by touching marker files)
  error_message := $(shell $(MAKE) build_avoidance)
  ifneq ($(error_message),)
    $(error $(error_message))
  endif
  $(info Build avoidance pass complete)
endif
