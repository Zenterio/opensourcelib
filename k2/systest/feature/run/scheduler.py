from zaf.component.decorator import component, requires


@component()
@requires(zk2='Zk2')
def run_test_verdicts(zk2):

    def run(include=[], include_regex=[], exclude=[], exclude_regex=[]):
        return zk2(
            [
                'runcommand', 'testrunner', 'testfinder', 'testscheduler', 'testresults',
                'textreport'
            ], 'run systest.data.suites.test_verdicts '
            '{include} '
            '{include_regex} '
            '{exclude} '
            '{exclude_regex}'.format(
                include=' '.join(['--tests-include {inc}'.format(inc=inc) for inc in include]),
                include_regex=' '.join(
                    ["--tests-include-regex '{inc}'".format(inc=inc) for inc in include_regex]),
                exclude=' '.join(['--tests-exclude {excl}'.format(excl=excl) for excl in exclude]),
                exclude_regex=' '.join(
                    ["--tests-exclude-regex '{excl}'".format(excl=excl)
                     for excl in exclude_regex])))

    return run


@requires(run_test_verdicts='run_test_verdicts')
def test_include_single_test(run_test_verdicts):
    result = run_test_verdicts(include=['systest.data.suites.test_verdicts.test_success'])
    assert 'Total:   1' in result.stdout


@requires(run_test_verdicts='run_test_verdicts')
def test_multiple_includes(run_test_verdicts):
    result = run_test_verdicts(
        include=[
            'systest.data.suites.test_verdicts.test_success',
            'systest.data.suites.test_verdicts.test_failure'
        ])
    assert 'Total:   2' in result.stdout


@requires(run_test_verdicts='run_test_verdicts')
def test_include_test_module(run_test_verdicts):
    result = run_test_verdicts(include=['systest.data.suites.test_verdicts'])
    assert 'Total:   5' in result.stdout


@requires(run_test_verdicts='run_test_verdicts')
def test_include_regex_single_test(run_test_verdicts):
    result = run_test_verdicts(include_regex=['verdict.*success'])
    assert 'Total:   1' in result.stdout


@requires(run_test_verdicts='run_test_verdicts')
def test_include_regex_matching_multiple_tests(run_test_verdicts):
    result = run_test_verdicts(include_regex=['[es]$'])
    assert 'Total:   2' in result.stdout


@requires(run_test_verdicts='run_test_verdicts')
def test_include_multiple_regexes(run_test_verdicts):
    result = run_test_verdicts(include_regex=['verdict.*success', 'verdict.*failure'])
    assert 'Total:   2' in result.stdout


@requires(run_test_verdicts='run_test_verdicts')
def test_include_regex_matching_module(run_test_verdicts):
    result = run_test_verdicts(include_regex=['test_verdicts'])
    assert 'Total:   5' in result.stdout


@requires(run_test_verdicts='run_test_verdicts')
def test_exclude_single_test(run_test_verdicts):
    result = run_test_verdicts(exclude=['systest.data.suites.test_verdicts.test_success'])
    assert 'Total:   4' in result.stdout


@requires(run_test_verdicts='run_test_verdicts')
def test_multiple_excludes(run_test_verdicts):
    result = run_test_verdicts(
        exclude=[
            'systest.data.suites.test_verdicts.test_success',
            'systest.data.suites.test_verdicts.test_failure'
        ])
    assert 'Total:   3' in result.stdout


@requires(run_test_verdicts='run_test_verdicts')
def test_exclude_test_module(run_test_verdicts):
    result = run_test_verdicts(exclude=['systest.data.suites.test_verdicts'])
    assert 'Total:   0' in result.stdout


@requires(run_test_verdicts='run_test_verdicts')
def test_exclude_regex_single_test(run_test_verdicts):
    result = run_test_verdicts(exclude_regex=['verdict.*success'])
    assert 'Total:   4' in result.stdout


@requires(run_test_verdicts='run_test_verdicts')
def test_exclude_regex_matching_multiple_tests(run_test_verdicts):
    result = run_test_verdicts(exclude_regex=['[es]$'])
    assert 'Total:   3' in result.stdout


@requires(run_test_verdicts='run_test_verdicts')
def test_exclude_multiple_regexes(run_test_verdicts):
    result = run_test_verdicts(exclude_regex=['verdict.*success', 'verdict.*failure'])
    assert 'Total:   3' in result.stdout


@requires(run_test_verdicts='run_test_verdicts')
def test_exclude_regex_matching_module(run_test_verdicts):
    result = run_test_verdicts(exclude_regex=['test_verdicts'])
    assert 'Total:   0' in result.stdout
