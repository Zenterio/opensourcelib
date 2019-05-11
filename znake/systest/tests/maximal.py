import re
from zaf.component.decorator import requires


@requires(znake='ZnakeMaximal')
def test_venv(znake):
    znake('venv')
    znake.workspace.assert_file_exists('.venv/bin/activate')
    znake.workspace.assert_file_exists('build')
    znake.workspace.assert_file_exists('setup.py')
    znake.workspace.assert_file_exists('maximal/version.py')
    znake.workspace.assert_in_file('maximal/version.py', "'version': '3.14.15',")
    znake.workspace.assert_in_file('maximal/version.py', "'''ZMT-1234: A very good version''',")
    znake.workspace.assert_in_file('maximal/version.py', "'date': 'Tue, 14 Mar 2017 12:00:00 +0000',")


@requires(znake='ZnakeMaximal')
def test_static_arguments(znake):
    result = znake('static')
    assert 'seconds elapsed' in result.stdout, 'Flake8 --benchmark flag not applied correctly'
    assert re.search('^0$', result.stdout, flags=re.MULTILINE) is not None, 'PyDocStyle should print a 0 for the number of warnings'
    assert '4.' in result.stdout, 'iSort should print version'


@requires(znake='ZnakeMaximal')
def test_test_arguments(znake):
    znake('--coverage test')
    znake.workspace.assert_file_exists('.coverage')


@requires(znake='ZnakeMaximal')
def test_tests_flags_narrows_down_which_tests_are_executed(znake):
    result = znake('-e --tests test_systest1 systest')
    assert 'tests_flags test_systest' in result.stdout, result.stdout


@requires(znake='ZnakeMaximal')
def test_systest_and_baseline(znake):
    znake('systest')
    znake.workspace.assert_file_exists('build/baseline/baseline.txt')
    znake('baseline')
    znake.workspace.assert_file_exists('build/baseline2/baseline.txt')


@requires(znake='ZnakeMaximal')
def test_doc_html_generation(znake):
    result = znake('doc.user-guide.html')
    assert 'custom html command' in result.stdout, result.stdout
    znake.workspace.assert_file_exists('build/doc/user_guide/html/index.html')


@requires(znake='ZnakeMaximal')
def test_doc_pdf_generation(znake):
    result = znake('doc.user-guide.pdf')
    assert 'custom pdf command' in result.stdout, result.stdout
    znake.workspace.assert_file_exists('build/doc/user_guide/pdf/user_guide.pdf')


@requires(znake='ZnakeMaximal')
def test_doc_generation_generates_both_pdf_and_html(znake):
    znake('doc')
    znake.workspace.assert_file_exists('build/doc/user_guide/html/index.html')
    znake.workspace.assert_file_exists('build/doc/user_guide/pdf/user_guide.pdf')


@requires(znake='ZnakeMaximal')
def test_dot_separated_namespace_names_are_used_in_summary(znake):
    result = znake('test')
    assert 'test.local' in result.stdout, result.stdout
    assert 'test.test' in result.stdout, result.stdout


@requires(znake='ZnakeMaximal')
def test_top_level_namespace_names_are_used_in_summary(znake):
    result = znake('clean')
    assert 'clean' in result.stdout, result.stdout