
from zaf.component.decorator import requires


@requires(znake='ZnakeFails')
def test_static(znake):
    znake('static', expected_exit_code=1)


@requires(znake='ZnakeFails')
def test_test(znake):
    znake('test', expected_exit_code=1)


@requires(znake='ZnakeFails')
def test_check(znake):
    znake('check', expected_exit_code=1)


@requires(znake='ZnakeFails')
def test_systest_fails(znake):
    result = znake('systest', expected_exit_code=1)
    assert 'Znake summary:' in result.stdout
    assert '-  systest.systest (skipped)' in result.stdout
    assert '-    systest.local (failed)' in result.stdout
    assert '-      create_venv' in result.stdout
    assert '-        write_version_file' in result.stdout
    assert '-        write_requirements_file' in result.stdout
    assert '-        write_requirements_dev_file' in result.stdout
    assert 'Znake done: failure' in result.stdout


@requires(znake='ZnakeFails')
def test_isort_fails(znake):
    result = znake('static.isort', expected_exit_code=1)
    assert "Run 'znake format' to automatically sort includes" in result.stdout


@requires(znake='ZnakeFails')
def test_flake8_fails(znake):
    znake('static.flake8', expected_exit_code=1)


@requires(znake='ZnakeFails')
def test_isort_fails(znake):
    result = znake('static.yapf', expected_exit_code=1)
    assert "Run 'znake format' to automatically solve formatting problems" in result.stdout


@requires(znake='ZnakeFails')
def test_non_graceful_exit(znake):
    result = znake('--no-graceful check', expected_exit_code=-9)