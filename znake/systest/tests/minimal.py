
from zaf.component.decorator import requires


@requires(znake='ZnakeMinimal')
def test_venv(znake):
    znake('venv')
    znake.workspace.assert_file_exists('.venv/bin/activate')
    znake.workspace.assert_file_exists('build')
    znake.workspace.assert_file_exists('setup.py')
    znake.workspace.assert_file_exists('minimal/version.py')
    znake.workspace.assert_in_file('minimal/version.py', "'version': '0.1.1'")
    znake.workspace.assert_in_file('minimal/version.py', "'''ZMT-1234: A change''',")
    znake.workspace.assert_in_file('minimal/version.py', "'date': 'Tue, 14 Mar 2017 12:00:00 +0000',")


@requires(znake='ZnakeMinimal')
def test_clean(znake):
    znake('venv')
    znake('clean')
    znake.workspace.assert_file_exists('.venv/bin/activate')
    znake.workspace.assert_file_not_exists('build')
    znake.workspace.assert_file_exists('setup.py')
    znake.workspace.assert_file_exists('minimal/version.py')


@requires(znake='ZnakeMinimal')
def test_static(znake):
    znake('static')


@requires(znake='ZnakeMinimal')
def test_format(znake):
    znake('format')


@requires(znake='ZnakeMinimal')
def test_test_coverage(znake):
    znake('--coverage test')
    znake.workspace.assert_file_exists('build/coverage/.coverage-local')
    znake.workspace.assert_file_exists('build/coverage/coverage-local.xml')


@requires(znake='ZnakeMinimal')
def test_check(znake):
    znake('check')


@requires(znake='ZnakeMinimal')
def test_systest(znake):
    znake('systest')
    znake.workspace.assert_file_exists('build/test/output-local/reports/testng/testng-results.xml')


@requires(znake='ZnakeMinimal')
def test_summary(znake):
    result = znake('static')
    assert 'Znake summary' in result.stdout


@requires(znake='ZnakeMinimal')
def test_no_summary(znake):
    result = znake('--no-summary static')
    assert 'Znake summary' not in result.stdout


@requires(znake='ZnakeMinimal')
def test_doc_html_generation(znake):
    result = znake('doc.user-guide.html')
    assert 'bin/sphinx-build' in result.stdout, result.stdout
    znake.workspace.assert_file_exists('build/doc/user_guide/html/index.html')
