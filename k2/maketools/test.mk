SYSTEST_PARALLEL_WORKERS := $(shell grep -c ^processor /proc/cpuinfo)

ADDON_SYSTESTS := $(shell find addons -type f -wholename '*/systest/*.py' -prune -not -wholename '*/systest/data/*.py')
CORE_SYSTESTS := $(wildcard systest/feature/*.py) $(wildcard systest/feature/*/*.py)
FEATURE_SYSTESTS := $(CORE_SYSTESTS) $(ADDON_SYSTESTS)
DEBPACKAGE_SYSTESTS := $(wildcard systest/debtest/*.py) $(wildcard systest/debtest/*/*.py)
BENCHMARK_SYSTESTS := $(wildcard systest/benchmark/*.py) $(wildcard systest/benchmark/*/*.py)
DEB_SYSTESTS := $(CORE_SYSTESTS) $(DEBPACKAGE_SYSTESTS)
ADDITIONAL_SYSTEST_ARGUMENTS :=

# Because we want to be able use 'test' in the name of things this
# is used to make what nosetests considers unittest classes/modules/methods
# more narrowly defined
UNIT_TEST_PATTERN = '^Test|^test_|\.test_|\.test\.'


# Defines targets for running tests on a node.
#
# Runs ZK2 in a local virtual Python environment.
#
# $(1) - Name of the node
define TEST

.PHONY: test_$(1)
test_$(1): SHELL := $$(NODE_$(1)_SHELL)
test_$(1): .SHELLFLAGS := $$(NODE_$(1)_SHELLFLAGS)
test_$(1): prepare_node_$(1)
	zk2 --log-level off --ext-logdefaults@enabled false unittest $$(if $$(filter $$(COVERAGE),y),--coverage-enabled --coverage-file .coverage-$(1) $$(if $$(filter $$(COVERAGE_XML_REPORT),y),--coverage-xml-enabled))

test_all: test_$(1)

.PHONY: systest_$(1)
systest_$(1): SHELL := $$(NODE_$(1)_SHELL)
systest_$(1): .SHELLFLAGS := $$(NODE_$(1)_SHELLFLAGS)
systest_$(1): prepare_node_$(1) cleancov_systest
	zk2 $$(ADDITIONAL_SYSTEST_ARGUMENTS) --output-dir $$(OUTPUT_DIR)-$(1) --config-file-pattern systest/systest_config.yaml run --parallel-workers $(SYSTEST_PARALLEL_WORKERS) --exitcode-from-verdict true $$(if $$(filter $$(COVERAGE),y), --coverage-enabled --coverage-report .coverage-systest-$(1) --coverage-config-file .coveragerc $$(if $$(filter $$(COVERAGE_XML_REPORT),y),--coverage-xml-report coverage-systest.xml)) $$(if $$(filter $$(SYSTEST_REPORT),y),--reports-testng true --reports-junit true) --suite-name k2.systest.$(1) $$(FEATURE_SYSTESTS)

systest_all: systest_$(1)

.PHONY: static_$(1)
static_$(1): SHELL := $(NODE_local_SHELL)
static_$(1): .SHELLFLAGS := $(NODE_local_SHELLFLAGS)
static_$(1): prepare_node_local
	@flake8 k2 systest addons || (echo "Run 'make format' to automatically solve most formatting problems" && exit 1)
	@pydocstyle k2 systest addons --ignore=D1,D202,D203,D204,D212 --match '.*\.py' --match-dir='^((?!generated|syntaxerror).)*$$$$' --explain
	@.venv/bin/yapf -p --style .yapf --diff $$(FORMAT_SOURCES) || (echo "Run 'make format' to automatically solve formatting problems" && exit 1)
	@.venv/bin/isort --multi-line 2 --check-only --dont-skip '__init__.py' --line-width 100 --thirdparty zaf $$(FORMAT_SOURCES) || (echo "Run 'make format' to automatically sort includes" && exit 1)

# For more information about pydocstyle, please see:
# http://www.pydocstyle.org/en/2.1.1/error_codes.html
# https://www.python.org/dev/peps/pep-0257/

static_all: static_$(1)

.PHONY: benchmark_$(1)
benchmark_$(1): SHELL := $$(NODE_$(1)_SHELL)
benchmark_$(1): .SHELLFLAGS := $$(NODE_$(1)_SHELLFLAGS)
benchmark_$(1): prepare_node_$(1) cleancov_systest $$(BENCHMARK_SYSTESTS)
	zk2 --config-file-pattern systest/benchmark_config.yaml run $$(BENCHMARK_SYSTESTS)
	@cat .benchmark

benchmark_all: benchmark_$(1)

.PHONY clean_systest: clean_$(1)
clean_$(1):
	rm -rf $$(OUTPUT_DIR)-$(1)

endef

$(eval $(foreach __node,$(TEST_NODES),$(call TEST,$(__node))))


# Defines convenience targets for running tests only on Docker nodes.
#
# $(1) - Name of the node
define DOCKER_TEST

test_docker: test_$(1)
systest_docker: systest_$(1)
static_docker: static_$(1)
benchmark_docker: benchmark_$(1)

endef

$(eval $(foreach __node,$(DOCKER_TEST_NODES),$(call DOCKER_TEST,$(__node))))


# Defines targets for running tests on a node.
#
# Runs ZK2 by installing it system-wide.
#
# $(1) - Name of the node
define DEB_TEST

.PHONY: debtest_$(2)
debtest_$(NODE_$(1)_CODENAME): SHELL := $$(NODE_$(1)_SHELL)
debtest_$(NODE_$(1)_CODENAME): .SHELLFLAGS := $$(NODE_$(1)_SHELLFLAGS)
debtest_$(NODE_$(1)_CODENAME): BASH_ENV :=
debtest_$(NODE_$(1)_CODENAME): $$($(1)_deb_builder_DIST) ./docker/markers/docker_node_$(1)_built.marker
	sudo apt-get update && \
	sudo gdebi --quiet --non-interactive $$$$(ls -t ./dist/$$(NODE_$(1)_CODENAME)/*.deb | head -1) && \
	zk2 $$(ADDITIONAL_SYSTEST_ARGUMENTS) --output-dir $$(OUTPUT_DIR)-$(1) --config-file-pattern systest/systest_config.yaml run --parallel-workers $(SYSTEST_PARALLEL_WORKERS) --exitcode-from-verdict true $$(if $$(filter $$(SYSTEST_REPORT),y),--reports-testng true  --reports-junit true) --suite-name k2.debtest.$(1) $$(DEB_SYSTESTS)

debtest: debtest_$(NODE_$(1)_CODENAME)

endef

$(eval $(foreach __node,$(DOCKER_TEST_NODES),$(call DEB_TEST,$(__node))))


.PHONY: cleancov_systest
cleancov_systest:
	@rm -f .coverage-systest*

.PHONY: cleancov
cleancov: cleancov_systest
	@rm -f .coverage .coverage-* .coverage.*
	@rm -f coverage*
