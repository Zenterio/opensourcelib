import os

from zaf.component.decorator import requires

DOCKER_MOCK = '{cwd}/systest/data/docker_mock.sh'.format(cwd=os.getcwd())


@requires(zebra='Zebra')
def test_shell_calls_bash(zebra):

    process = zebra('-v shell')

    assert '/bin/bash -c /bin/bash' in process.stdout
