import os
from tempfile import TemporaryDirectory

from zaf.component.decorator import requires


@requires(zafapp='ZafApp')
def test_unittests_for_extension(zafapp):
    result = zafapp(
        ['unittestcommand', 'extensionwithunittests'], '--log-level debug '
        '--config-file-pattern systest/data/simple_config.yaml '
        'unittest --no-unittest-exclude-systest extensionwithunittests', 1)
    assert 'Ran 3 tests' in result.stderr


@requires(zafapp='ZafApp')
def test_unittests_for_package_with_test_option(zafapp):
    result = zafapp(
        ['unittestcommand', 'extensionwithunittests'], '--log-level debug '
        '--config-file-pattern systest/data/simple_config.yaml '
        'unittest --no-unittest-exclude-systest '
        '--tests extension_with_unittests.test', 1)
    assert 'Ran 3 tests' in result.stderr


@requires(zafapp='ZafApp')
def test_unittest_with_test_option_with_successful_tests(zafapp):
    result = zafapp(
        ['unittestcommand', 'extensionwithunittests'], '--log-level debug '
        '--config-file-pattern systest/data/simple_config.yaml '
        'unittest --no-unittest-exclude-systest '
        '--tests systest/data/plugins/extension_with_unittests/test/test_success.py', 0)
    assert 'Ran 2 tests' in result.stderr


@requires(zafapp='ZafApp')
def test_unittest_with_test_option_with_failing_test(zafapp):
    result = zafapp(
        ['unittestcommand', 'extensionwithunittests'], '--log-level debug '
        '--config-file-pattern systest/data/simple_config.yaml '
        'unittest --no-unittest-exclude-systest '
        '--tests systest/data/plugins/extension_with_unittests/test/test_fail.py', 1)
    assert 'Ran 1 test' in result.stderr


@requires(zafapp='ZafApp')
def test_unittest_with_multiple_test_options(zafapp):
    result = zafapp(
        ['unittestcommand', 'extensionwithunittests'], '--log-level debug '
        '--config-file-pattern systest/data/simple_config.yaml '
        'unittest --no-unittest-exclude-systest '
        '--tests systest/data/plugins/extension_with_unittests/test/test_success.py '
        '--tests extension_with_unittests.test.test_fail', 1)
    assert 'Ran 3 tests' in result.stderr


@requires(zafapp='ZafApp')
def test_unittest_for_specific_test_case(zafapp):
    result = zafapp(
        ['unittestcommand', 'extensionwithunittests'], '--log-level debug '
        '--config-file-pattern systest/data/simple_config.yaml '
        'unittest --no-unittest-exclude-systest '
        '--tests extension_with_unittests.test.test_success:test_success1', 0)
    assert 'Ran 1 test' in result.stderr


@requires(zafapp='ZafApp')
def test_unittest_with_report(zafapp):
    with TemporaryDirectory() as tmpdir:
        result = zafapp(
            ['unittestcommand', 'extensionwithunittests'],
            '--log-level debug '
            '--config-file-pattern systest/data/simple_config.yaml '
            'unittest --no-unittest-exclude-systest extensionwithunittests '
            '--report-enabled --report-file {dir}/report.xml'.format(dir=tmpdir),
            1)
        assert 'Ran 3 tests' in result.stderr
        assert os.path.exists(os.path.join(tmpdir, 'report.xml'))


@requires(zafapp='ZafApp')
def test_unittest_with_coverage(zafapp):
    with TemporaryDirectory() as tmpdir:
        result = zafapp(
            ['unittestcommand', 'extensionwithunittests'],
            '--config-file-pattern systest/data/simple_config.yaml '
            'unittest --no-unittest-exclude-systest extensionwithunittests --coverage-enabled '
            '--coverage-file {dir}/.coverage'.format(dir=tmpdir),
            1)
        assert 'extension_with_unittests/extension_with_unittests.py' in result.stdout
        assert 'Ran 3 tests' in result.stderr
        assert os.path.exists(os.path.join(tmpdir, '.coverage'))


@requires(zafapp='ZafApp')
def test_unittest_with_coverage_xml_report(zafapp):
    with TemporaryDirectory() as tmpdir:
        result = zafapp(
            ['unittestcommand', 'extensionwithunittests'],
            '--log-level debug '
            '--config-file-pattern systest/data/simple_config.yaml '
            'unittest --no-unittest-exclude-systest extensionwithunittests --coverage-enabled '
            '--coverage-file {dir}/.coverage '
            '--coverage-xml-enabled --coverage-xml-file {dir}/coverage.xml'.format(dir=tmpdir),
            1)
        assert 'Ran 3 tests' in result.stderr
        assert os.path.exists(os.path.join(tmpdir, '.coverage'))
        assert os.path.exists(os.path.join(tmpdir, 'coverage.xml'))
