PYPI_TARGETS := setup.py $(shell find addons -name 'setup.py')


pypi_sdist_dir:
	mkdir -p pypi/sdist

pypi_sdist: SHELL := $(NODE_local_SHELL)
pypi_sdist: .SHELLFLAGS := $(NODE_local_SHELLFLAGS)
pypi_sdist: prepare_node_local pypi_sdist_dir
pypi_sdist:
	for target in $(PYPI_TARGETS); do \
		pushd $$(dirname $$target) && BUILD_NUMBER=${BUILD_NUMBER} python3 setup.py sdist -d "$(abspath pypi/sdist)" && popd; \
	done

pypi_sdist_clean:
	rm -rf k2_*.egg-info

pypi_sdist_cleanup: pypi_sdist_clean
	rm -rf pypi/sdist


pypi_wheel_dir:
	mkdir -p pypi/wheel

pypi_wheel: SHELL := $(NODE_manylinux_wheel_builder_SHELL)
pypi_wheel: .SHELLFLAGS := $(NODE_manylinux_wheel_builder_SHELLFLAGS)
pypi_wheel: BASH_ENV :=
pypi_wheel: ./docker/markers/docker_node_manylinux_wheel_builder_built.marker pypi_wheel_dir
pypi_wheel:
	for target in $(PYPI_TARGETS); do \
		pushd $$(dirname $$target) && BUILD_NUMBER=${BUILD_NUMBER} /opt/python/cp35-cp35m/bin/python3 setup.py bdist_wheel -d "$(abspath pypi/wheel)" && popd; \
	done

pypi_wheel_clean:
	rm -rf build

pypi_wheel_cleanup: pypi_wheel_clean
	rm -rf pypi/wheel


pypi: pypi_sdist pypi_wheel
clean_pypi: pypi_sdist_clean pypi_wheel_clean
cleanup_pypi: pypi_sdist_cleanup pypi_wheel_cleanup
