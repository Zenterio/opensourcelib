import os

from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_plugin_that_sends_requests(zk2):

    result = zk2(
        ['runcommand', 'testrunner', 'testfinder', 'testscheduler', 'printrunqueueaftereachtest'],
        'run systest.data.suites.test_simple',
        plugin_path=os.path.join('systest', 'data', 'plugins'))

    assert 'Run queue: [systest.data.suites.test_simple.test_my_test_case]' in result.stdout \
           or 'Run queue: [systest.data.suites.test_simple.test_my_other_test_case]' in result.stdout
    assert 'Run queue: []' in result.stdout
