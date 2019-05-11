import os

from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_instantiate_extensions(zk2):
    result = zk2(
        ['runcommand', 'testfinder', 'instantiated'],
        'run systest.data.suites.test_minimal '
        '--instances-ids a --instances-ids b '
        '--instances-a@dependent-option 1 --instances-b@dependent-option 2',
        plugin_path=os.path.join('systest', 'data', 'plugins'))

    assert 'a: dependent.option: 1' in result.stdout
    assert 'b: dependent.option: 2' in result.stdout
