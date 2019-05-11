import os

from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_list(zk2):
    result = zk2(['listcommand', 'testfinder'], 'list systest.data.suites')

    assert 'test_my_test_case' in result.stdout


@requires(zk2='Zk2')
def test_list_with_instanced_extension(zk2):
    result = zk2(
        ['instantiated', 'listcommand', 'testfinder'],
        'list systest.data.suites',
        plugin_path=os.path.join('systest', 'data', 'plugins'))

    assert 'test_my_test_case' in result.stdout
