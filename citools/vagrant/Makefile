
#
# Makefile for creating Zenterio CI Staging environment Vagrant box
#
SHELL := /bin/bash


.PHONY: default_target
default_target: help

BOX_NAME := zenterio-ci-staging
BOX_FILE_NAME := $(BOX_NAME).box
VAGRANT_CATALOG_SERVER := vagrant.zenterio.lan

.PHONY: help
help:
	@cat README

.PHONY: clean
clean: cleanbox
	vagrant destroy --force


.PHONY: cleanbox
cleanbox:
	rm -f $(BOX_FILE_NAME)


.PHONY: up
up:
	vagrant up

.PHONY: prepare
prepare:
	@$(MAKE) prepare-stage-1
	@$(MAKE) prepare-stage-2

.PHONY: prepare-stage-1
prepare-stage-1:
	vagrant ssh -c "sudo /vagrant/vagrant/prepare_for_packaging_stage_1"

.PHONY: prepare-stage-2
prepare-stage-2:
	vagrant ssh -c "sudo /vagrant/vagrant/prepare_for_packaging_stage_2"

.PHONY: package
package: check-change-log
	@$(MAKE) cleanbox
	vagrant snapshot push
	vagrant up
	@$(MAKE) prepare-stage-1
	vagrant halt
	sleep 5
	vagrant up
	@$(MAKE) prepare-stage-2
	sleep 15
	vagrant halt || true
	@$(MAKE) $(BOX_FILE_NAME)
	vagrant snapshot pop

$(BOX_FILE_NAME):
	vagrant package --vagrantfile include/Vagrantfile --output "$@"

.PHONY: check-change-log
check-change-log:
	@source ./vagrantlib; \
	export VERSION="$$(next_version "$(BOX_NAME)")"; \
	grep -q -e "^$${VERSION} (.*)\$$" CHANGELOG || { echo "The CHANGELOG is missing entry for next version ($${VERSION})" && exit 1; }

.PHONY: deploy
deploy:
	@test -f $(BOX_FILE_NAME) || { echo "The box-file $(BOX_FILE_NAME) doesn't exist. Please run: make package" && exit 1; }
	@echo "Uploading $(BOX_FILE_NAME), no progress will be printed."
	@source vagrantlib; ./deploy_to_vagrant_repository "$(BOX_FILE_NAME)" "$$(next_version $(BOX_NAME))" "$(BOX_NAME)"


.PHONY: list-box-versions
list-box-versions:
	@source ./vagrantlib; all_versions "$(BOX_NAME)"

.PHONY: list-next-version
list-next-version:
	@source ./vagrantlib; next_version "$(BOX_NAME)"
