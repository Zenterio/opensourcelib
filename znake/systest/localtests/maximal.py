from zaf.component.decorator import requires


@requires(znake='ZnakeMaximal')
def test_debtest(znake):
    znake('debtest')
    znake.workspace.assert_file_exists('build/dist/bionic/zenterio-zmaximal_3.14.15+0+bionic_amd64.deb')
    znake.workspace.assert_file_not_exists('build/dist/xenial/zenterio-zmaximal_3.14.15+0+xenial_amd64.deb')


@requires(znake='ZnakeMaximal')
def test_debtest_does_not_exist_for_target_without_test_image(znake):
    znake('debtest.u16', expected_exit_code=1)


@requires(znake='ZnakeMaximal')
def test_pypi(znake):
    znake('pypi')
    znake.workspace.assert_file_exists('build/pypi/sdist/zenterio-zmaximal-3.14.15+0.tar.gz')
    znake.workspace.assert_file_exists('build/pypi/wheel/zenterio_zmaximal-3.14.15+0-py3-none-any.whl')


@requires(znake='ZnakeMaximal')
def test_test_for_targets(znake):
    znake('test.u14', expected_exit_code=1)
    znake('test.u16')
