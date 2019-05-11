BUILD_DIR := build

include maketools/docker.mk
include maketools/build_avoidance.mk
include maketools/lint.mk
include maketools/test.mk
include maketools/help.mk

all: images

check: lint
