from zaf.component.decorator import requires


@requires(zk2='Zk2')
def test_help(zk2):
    zk2([], '--help')


@requires(zk2='Zk2')
def test_version(zk2):
    zk2([], '--version')
