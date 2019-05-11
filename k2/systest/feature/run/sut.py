from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_cans_can_be_added_to_sut(zk2):
    extensions = ['sut', 'runcommand', 'testrunner', 'testfinder', 'testscheduler']
    result_a = zk2(
        extensions, 'run --suts-ids a --suts-a@add-can a '
        'systest.data.suites.test_sut')
    assert 'a' in result_a.stdout, result_a.stdout
    assert 'b' not in result_a.stdout, result_a.stdout

    result_b = zk2(
        extensions, 'run --suts-ids b --suts-b@add-can b '
        'systest.data.suites.test_sut')
    assert 'a' not in result_b.stdout, result_b.stdout
    assert 'b' in result_b.stdout, result_b.stdout
