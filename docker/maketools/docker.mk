DOCKER_REGISTRY ?= docker.zenterio.lan
DOCKER_DIRECTORY ?= zenterio
DOCKER_IMAGES := $(notdir $(wildcard images/*))

IMAGE_TAG ?= latest
DOCKER_REGISTRY_USERNAME ?=
DOCKER_REGISTRY_PASSWORD ?=
DOCKER_BUILD_FLAGS ?=
NOOP ?=
COMMANDS_PREFIX ?=

BUILT_IMAGES_DIR := $(BUILD_DIR)/built_images

ifeq ($(NOOP),y)
COMMANDS_PREFIX := echo
endif

define NEW_LINE


endef

# Returns path to the Dockerfile with the specified name
#
# $1 name of image
define DOCKER_FILE
images/$(1)/Dockerfile
endef

# Returns <prefix><image name> for dependency of the specified image
#
# $1 name of image
# $2 prefix
define IMAGE_PARENT_WITH_PREFIX
$(foreach __image,$(strip $(filter $(DOCKER_IMAGES),$(shell grep 'FROM ' $(call DOCKER_FILE,$(1)) | grep -o '[^/]*$$'))),$(2)$(__image))
endef

# Calculate the make target of the image that this image depends on
# This is done by parsing the name of the image from the FROM statement
# in the Dockerfile and then check that it is part of DOCKER_IMAGES.
#
# $1 name of image
define IMAGE_PARENT_AS_DEPENDENCY
$(foreach __image,$(strip $(filter $(DOCKER_IMAGES),$(shell grep 'FROM ' $(call DOCKER_FILE,$(1)) | grep -o '[^/]*$$'))),$(BUILD_DIR)/$(__image).marker)
endef

# Creates an image locally
# The complete image name is $(DOCKER_REGISTRY)/$(DOCKER_DIRECTORY)/$(name):$(IMAGE_TAG)
# The IMAGE_TAG varible can be overridden to specify another tag than LATEST.
#
# $1 name of image
#
define CREATE_IMAGE
__depends_on_$(1) := $(call IMAGE_PARENT_AS_DEPENDENCY,$(1))

image_$(1): $(BUILD_DIR)/$(1).marker
$(BUILD_DIR)/$(1).marker: $(shell find images/$(1) -type f | sed -e 's/ /\\ /') $$(__depends_on_$(1)) | $(BUILD_DIR) $(BUILT_IMAGES_DIR)
ifeq ($$(__depends_on_$(1)),)
	$(COMMANDS_PREFIX) docker build --tag $(DOCKER_REGISTRY)/$(DOCKER_DIRECTORY)/$(1):latest $(DOCKER_BUILD_FLAGS) --pull --no-cache images/$(1)/
else
#Depends on local image so we shouldn't pull from registry
	$(COMMANDS_PREFIX) docker build --tag $(DOCKER_REGISTRY)/$(DOCKER_DIRECTORY)/$(1):latest $(DOCKER_BUILD_FLAGS) --no-cache images/$(1)/
endif
	touch $$@
	touch $(BUILT_IMAGES_DIR)/$(1)

ifneq ($(firstword $(subst ., ,$1)),$1)
images_$(firstword $(subst ., ,$1)): $(BUILD_DIR)/$(1).marker
image_$(firstword $(subst ., ,$1)): $(BUILD_DIR)/$(1).marker
endif

images: $(BUILD_DIR)/$(1).marker
image: $(BUILD_DIR)/$(1).marker

endef

# Tags $(DOCKER_REGISTRY)/$(DOCKER_DIRECTORY)/$(name):latest with $(DOCKER_REGISTRY)/$(DOCKER_DIRECTORY)/$(name):$(IMAGE_TAG)
#
# $1 name of image
#
define TAG_IMAGE

ifneq ($(firstword $(subst ., ,$1)),$1)
tag_$(firstword $(subst ., ,$1)): tag_$(1)
endif
tag_$(1): $(BUILD_DIR)/$(1).marker
	$(COMMANDS_PREFIX) docker tag $(DOCKER_REGISTRY)/$(DOCKER_DIRECTORY)/$(1):latest $(DOCKER_REGISTRY)/$(DOCKER_DIRECTORY)/$(1):$(IMAGE_TAG)
endef

# Pushes an image to the docker registry
# The complete image name is $(DOCKER_REGISTRY)/$(DOCKER_DIRECTORY)/$(name):$(IMAGE_TAG)
# The IMAGE_TAG varible can be overridden to specify another tag than LATEST.
# $1 name of image
#
define PUSH_IMAGE

ifneq ($(firstword $(subst ., ,$1)),$1)
push_$(firstword $(subst ., ,$1)): push_$(1)
endif
push_$(1): tag_$(1) login
	$(COMMANDS_PREFIX) docker push $(DOCKER_REGISTRY)/$(DOCKER_DIRECTORY)/$(1):$(IMAGE_TAG)

endef

# Create clean and cleanup targets
# Clean cleans the image from the build directory and cleanup also
# removes the local docker image.
#
# Cleanup uses the IMAGE_TAG so it can be used to cleanup non-latest tags also
# If the specified IMAGE_TAG is latest cleanup will also perform clean
#
# $1 name of image
#
define CLEAN_AND_CLEANUP_IMAGE_WITH_TAG

cleanup: cleanup_$(1)
ifneq ($(firstword $(subst ., ,$1)),$1)
cleanup_$(firstword $(subst ., ,$1)): cleanup_$(1)
endif
cleanup_$(1): $(if $(filter $(IMAGE_TAG),latest),clean_$(1))
	$(COMMANDS_PREFIX) docker rmi -f $(DOCKER_REGISTRY)/$(DOCKER_DIRECTORY)/$(1):$(IMAGE_TAG)

clean: clean_$(1)
ifneq ($(firstword $(subst ., ,$1)),$1)
clean_$(firstword $(subst ., ,$1)): clean_$(1)
endif
clean_$(1):
	$(COMMANDS_PREFIX) rm -f $(BUILD_DIR)/$(1).marker
	$(COMMANDS_PREFIX) rm -f $(BUILT_IMAGES_DIR)/$(1)

endef


# Tag and push targets are created to only tag and push images
# that were actually built locally. This works with the build avoidance
# functionality and also with running a more specific image_<image name> target.
#
# When building an image build/built_images/<image_name> is touched to indicate
# that the image was actually built. This is because the build/<image>.marker files
# are used also for build avoidance.
#
# tag and push will be run on all images in build/built_images
tag: $(foreach __image,$(notdir $(strip $(wildcard $(BUILT_IMAGES_DIR)/*))),tag_$(__image)) | $(BUILT_IMAGES_DIR)
push: $(foreach __image,$(notdir $(strip $(wildcard $(BUILT_IMAGES_DIR)/*))),push_$(__image)) | $(BUILT_IMAGES_DIR)

$(eval $(foreach __dockerimage,$(DOCKER_IMAGES),$(call CREATE_IMAGE,$(__dockerimage))$(NEW_LINE)))
$(eval $(foreach __dockerimage,$(DOCKER_IMAGES),$(call TAG_IMAGE,$(__dockerimage))$(NEW_LINE)))
$(eval $(foreach __dockerimage,$(DOCKER_IMAGES),$(call PUSH_IMAGE,$(__dockerimage))$(NEW_LINE)))
$(eval $(foreach __dockerimage,$(DOCKER_IMAGES),$(call CLEAN_AND_CLEANUP_IMAGE_WITH_TAG,$(__dockerimage))$(NEW_LINE)))

login:
	@$(COMMANDS_PREFIX) test $(DOCKER_REGISTRY_USERNAME) || (echo Error logging in to docker registry, DOCKER_REGISTRY_USERNAME not specified && exit 1)
	@$(COMMANDS_PREFIX) test $(DOCKER_REGISTRY_PASSWORD) || (echo Error logging in to docker registry, DOCKER_REGISTRY_PASSWORD not specified && exit 1)
	@$(COMMANDS_PREFIX) docker login --username $(DOCKER_REGISTRY_USERNAME) --password $(DOCKER_REGISTRY_PASSWORD) $(DOCKER_REGISTRY)

$(BUILD_DIR):
	@mkdir -p $@


$(BUILT_IMAGES_DIR): | $(BUILD_DIR)
	@mkdir -p $@
