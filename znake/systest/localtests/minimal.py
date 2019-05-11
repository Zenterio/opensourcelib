from zaf.component.decorator import requires


@requires(znake='ZnakeMinimal')
def test_debtest(znake):
    znake('debtest')
    znake.workspace.assert_file_exists('build/dist/trusty/zenterio-zminimal_0.1.1+0+trusty_amd64.deb')
    znake.workspace.assert_file_exists('build/dist/xenial/zenterio-zminimal_0.1.1+0+xenial_amd64.deb')
    znake.workspace.assert_file_exists('build/dist/bionic/zenterio-zminimal_0.1.1+0+bionic_amd64.deb')


@requires(znake='ZnakeMinimal')
def test_pypi(znake):
    znake('pypi')
    znake.workspace.assert_file_exists('build/pypi/sdist/zenterio-zminimal-0.1.1+0.tar.gz')
    znake.workspace.assert_file_exists('build/pypi/wheel/zenterio_zminimal-0.1.1+0-py3-none-any.whl')


@requires(znake='ZnakeMinimal')
def test_test_in_docker(znake):
    znake('test.u16')


@requires(znake='ZnakeMinimal')
def test_systest_in_docker(znake):
    znake('systest.u16')
    znake.workspace.assert_file_exists('build/test/output-u16/reports/testng/testng-results.xml')


@requires(znake='ZnakeMinimal')
def test_cleanup(znake):
    znake('venv')
    znake('cleanup')
    znake.workspace.assert_file_not_exists('.venv/bin/activate')
    znake.workspace.assert_file_not_exists('build')
    znake.workspace.assert_file_not_exists('setup.py')
    znake.workspace.assert_file_not_exists('minimal/version.py')


@requires(znake='ZnakeMinimal')
def test_doc_pdf_generation(znake):
    result = znake('doc.user-guide.pdf')
    assert 'bin/sphinx-build' in result.stdout, result.stdout
    znake.workspace.assert_file_exists('build/doc/user_guide/pdf/user_guide.pdf')


@requires(znake='ZnakeMinimal')
def test_doc_generation_generates_both_pdf_and_html(znake):
    znake('doc')
    znake.workspace.assert_file_exists('build/doc/user_guide/html/index.html')
    znake.workspace.assert_file_exists('build/doc/user_guide/pdf/user_guide.pdf')
