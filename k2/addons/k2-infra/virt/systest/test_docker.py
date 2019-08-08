import os
from tempfile import TemporaryDirectory
from textwrap import dedent

from zaf.component.decorator import component, requires

from k2.runner.exceptions import SkipException


@component(name='SkipIfDockerIsNotInstalled')
@requires(exec='Exec', can=('host', ))
@requires(infra='Infra', uses=('exec', ))
def skip_if_docker_is_not_installed(exec, infra):
    if not infra.package('docker-ce').is_installed:
        raise SkipException('The docker-ce package is not installed')
    if not infra.service('docker').is_running:
        raise SkipException('The docker service is not running')


@component(name='BuildDockerImage', scope='session')
@requires(prereq='SkipIfDockerIsNotInstalled')
@requires(process_runner='ProcessRunner')
def build_docker_image(process_runner):
    with TemporaryDirectory() as dir:
        with open(os.path.join(dir, 'Dockerfile'), 'w') as f:
            f.write(
                dedent(
                    """\
                FROM docker.zenterio.lan/library/busybox
                CMD ["/bin/sh", "-c", "sleep 60"]
                """))

        process_runner(f'docker build --tag docker.zenterio.lan/zenterio/k2testimage {dir}')


@requires(prereq='SkipIfDockerIsNotInstalled')
@requires(image='BuildDockerImage')
@requires(zk2='Zk2')
def test_node(prereq, zk2):
    result = zk2(
        [
            'sut', 'docker', 'runcommand', 'testrunner', 'testfinder', 'testscheduler',
            'testresults', 'textreport'
        ],
        'run '
        '--suts-ids mynode '
        '--suts-mynode@docker-image k2testimage '
        '--docker-images-ids k2testimage '
        '--docker-images-k2testimage@repository docker.zenterio.lan/zenterio/k2testimage '
        '--docker-images-k2testimage@tag latest '
        '--no-docker-image-pull '
        '--docker-image-stop-timeout 0 '
        'virt.systest.data.suites.test_docker:test_node ',
        timeout=80)

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout


@requires(prereq='SkipIfDockerIsNotInstalled')
@requires(image='BuildDockerImage')
@requires(zk2='Zk2')
def test_node_with_hostname_specified_for_image(prereq, zk2):
    result = zk2(
        [
            'sut', 'docker', 'runcommand', 'testrunner', 'testfinder', 'testscheduler',
            'testresults', 'textreport'
        ],
        'run '
        '--suts-ids mynode '
        '--suts-mynode@docker-image k2testimage '
        '--docker-images-ids k2testimage '
        '--docker-images-k2testimage@repository docker.zenterio.lan/zenterio/k2testimage '
        '--docker-images-k2testimage@tag latest '
        '--docker-images-k2testimage@hostname a '
        '--no-docker-image-pull '
        '--docker-image-stop-timeout 0 '
        'virt.systest.data.suites.test_docker:test_hostname_is_a ',
        timeout=80)

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout


@requires(prereq='SkipIfDockerIsNotInstalled')
@requires(image='BuildDockerImage')
@requires(zk2='Zk2')
def test_node_with_hostname_specified_for_sut(prereq, zk2):
    result = zk2(
        [
            'sut', 'docker', 'runcommand', 'testrunner', 'testfinder', 'testscheduler',
            'testresults', 'textreport'
        ],
        'run '
        '--suts-ids mynode '
        '--suts-mynode@docker-image k2testimage '
        '--suts-mynode@docker-hostname b '
        '--docker-images-ids k2testimage '
        '--docker-images-k2testimage@repository docker.zenterio.lan/zenterio/k2testimage '
        '--docker-images-k2testimage@tag latest '
        '--docker-images-k2testimage@hostname a '
        '--no-docker-image-pull '
        '--docker-image-stop-timeout 0 '
        'virt.systest.data.suites.test_docker:test_hostname_is_b ',
        timeout=80)

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout


@requires(prereq='SkipIfDockerIsNotInstalled')
@requires(image='BuildDockerImage')
@requires(zk2='Zk2')
def test_node_with_tmpfs_mount_specified_for_image(prereq, zk2):
    result = zk2(
        [
            'sut', 'docker', 'runcommand', 'testrunner', 'testfinder', 'testscheduler',
            'testresults', 'textreport'
        ],
        'run '
        '--suts-ids mynode '
        '--suts-mynode@docker-image k2testimage '
        '--docker-images-ids k2testimage '
        '--docker-images-k2testimage@repository docker.zenterio.lan/zenterio/k2testimage '
        '--docker-images-k2testimage@tag latest '
        '--docker-images-k2testimage@mountpoints type=tmpfs,target=/foo '
        '--no-docker-image-pull '
        '--docker-image-stop-timeout 0 '
        'virt.systest.data.suites.test_docker:test_foo_is_mounted_tmpfs ',
        timeout=80)

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout


@requires(prereq='SkipIfDockerIsNotInstalled')
@requires(image='BuildDockerImage')
@requires(zk2='Zk2')
def test_node_with_tmpfs_mount_specified_for_sut(prereq, zk2):
    result = zk2(
        [
            'sut', 'docker', 'runcommand', 'testrunner', 'testfinder', 'testscheduler',
            'testresults', 'textreport'
        ],
        'run '
        '--suts-ids mynode '
        '--suts-mynode@docker-image k2testimage '
        '--suts-mynode@docker-mountpoints type=tmpfs,target=/foo '
        '--docker-images-ids k2testimage '
        '--docker-images-k2testimage@repository docker.zenterio.lan/zenterio/k2testimage '
        '--docker-images-k2testimage@tag latest '
        '--no-docker-image-pull '
        '--docker-image-stop-timeout 0 '
        'virt.systest.data.suites.test_docker:test_foo_is_mounted_tmpfs ',
        timeout=80)

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout


@requires(prereq='SkipIfDockerIsNotInstalled')
@requires(image='BuildDockerImage')
@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_node_with_bind_mount_specified_for_image(prereq, zk2, workspace):
    source_path = workspace.create_dir('foo')
    result = zk2(
        [
            'sut', 'docker', 'runcommand', 'testrunner', 'testfinder', 'testscheduler',
            'testresults', 'textreport'
        ], (
            'run '
            '--suts-ids mynode '
            '--suts-mynode@docker-image k2testimage '
            '--docker-images-ids k2testimage '
            '--docker-images-k2testimage@repository docker.zenterio.lan/zenterio/k2testimage '
            '--docker-images-k2testimage@tag latest '
            '--docker-images-k2testimage@mountpoints type=bind,source={source_path},target=/foo '
            '--no-docker-image-pull '
            '--docker-image-stop-timeout 0 '
            'virt.systest.data.suites.test_docker:test_foo_is_mounted '
        ).format(source_path=source_path),
        timeout=80)

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout


@requires(prereq='SkipIfDockerIsNotInstalled')
@requires(image='BuildDockerImage')
@requires(zk2='Zk2')
@requires(workspace='Workspace')
def test_node_with_bind_mount_specified_for_sut(prereq, zk2, workspace):
    source_path = workspace.create_dir('foo')
    result = zk2(
        [
            'sut', 'docker', 'runcommand', 'testrunner', 'testfinder', 'testscheduler',
            'testresults', 'textreport'
        ], (
            'run '
            '--suts-ids mynode '
            '--suts-mynode@docker-image k2testimage '
            '--suts-mynode@docker-mountpoints type=bind,source={source_path},target=/foo '
            '--docker-images-ids k2testimage '
            '--docker-images-k2testimage@repository docker.zenterio.lan/zenterio/k2testimage '
            '--docker-images-k2testimage@tag latest '
            '--no-docker-image-pull '
            '--docker-image-stop-timeout 0 '
            'virt.systest.data.suites.test_docker:test_foo_is_mounted '
        ).format(source_path=source_path),
        timeout=80)

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout
