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


@requires(prereq='SkipIfDockerIsNotInstalled')
@requires(zk2='Zk2')
def test_node(prereq, zk2):
    result = zk2(
        [
            'sut', 'docker', 'runcommand', 'testrunner', 'testfinder', 'testscheduler',
            'testresults', 'textreport'
        ], 'run '
        '--suts-ids mynode '
        '--suts-mynode@docker-image puppetcentos7 '
        '--docker-images-ids puppetcentos7 '
        '--docker-images-puppetcentos7@repository docker.zenterio.lan/zenterio/puppet.centos7 '
        '--docker-images-puppetcentos7@tag latest '
        '--docker-image-pull '
        '--docker-image-stop-timeout 0 '
        'virt.systest.data.suites.test_docker:test_node ')

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout


@requires(prereq='SkipIfDockerIsNotInstalled')
@requires(zk2='Zk2')
def test_node_with_hostname_specified_for_image(prereq, zk2):
    result = zk2(
        [
            'sut', 'docker', 'runcommand', 'testrunner', 'testfinder', 'testscheduler',
            'testresults', 'textreport'
        ], 'run '
        '--suts-ids mynode '
        '--suts-mynode@docker-image puppetcentos7 '
        '--docker-images-ids puppetcentos7 '
        '--docker-images-puppetcentos7@repository docker.zenterio.lan/zenterio/puppet.centos7 '
        '--docker-images-puppetcentos7@tag latest '
        '--docker-images-puppetcentos7@hostname a '
        '--docker-image-pull '
        '--docker-image-stop-timeout 0 '
        'virt.systest.data.suites.test_docker:test_hostname_is_a ')

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout


@requires(prereq='SkipIfDockerIsNotInstalled')
@requires(zk2='Zk2')
def test_node_with_hostname_specified_for_sut(prereq, zk2):
    result = zk2(
        [
            'sut', 'docker', 'runcommand', 'testrunner', 'testfinder', 'testscheduler',
            'testresults', 'textreport'
        ], 'run '
        '--suts-ids mynode '
        '--suts-mynode@docker-image puppetcentos7 '
        '--suts-mynode@docker-hostname b '
        '--docker-images-ids puppetcentos7 '
        '--docker-images-puppetcentos7@repository docker.zenterio.lan/zenterio/puppet.centos7 '
        '--docker-images-puppetcentos7@tag latest '
        '--docker-images-puppetcentos7@hostname a '
        '--docker-image-pull '
        '--docker-image-stop-timeout 0 '
        'virt.systest.data.suites.test_docker:test_hostname_is_b ')

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout


@requires(prereq='SkipIfDockerIsNotInstalled')
@requires(zk2='Zk2')
def test_node_with_tmpfs_mount_specified_for_image(prereq, zk2):
    result = zk2(
        [
            'sut', 'docker', 'runcommand', 'testrunner', 'testfinder', 'testscheduler',
            'testresults', 'textreport'
        ], 'run '
        '--suts-ids mynode '
        '--suts-mynode@docker-image puppetcentos7 '
        '--docker-images-ids puppetcentos7 '
        '--docker-images-puppetcentos7@repository docker.zenterio.lan/zenterio/puppet.centos7 '
        '--docker-images-puppetcentos7@tag latest '
        '--docker-images-puppetcentos7@mountpoints type=tmpfs,target=/foo '
        '--docker-image-pull '
        '--docker-image-stop-timeout 0 '
        'virt.systest.data.suites.test_docker:test_foo_is_mounted_tmpfs ')

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout


@requires(prereq='SkipIfDockerIsNotInstalled')
@requires(zk2='Zk2')
def test_node_with_tmpfs_mount_specified_for_sut(prereq, zk2):
    result = zk2(
        [
            'sut', 'docker', 'runcommand', 'testrunner', 'testfinder', 'testscheduler',
            'testresults', 'textreport'
        ], 'run '
        '--suts-ids mynode '
        '--suts-mynode@docker-image puppetcentos7 '
        '--suts-mynode@docker-mountpoints type=tmpfs,target=/foo '
        '--docker-images-ids puppetcentos7 '
        '--docker-images-puppetcentos7@repository docker.zenterio.lan/zenterio/puppet.centos7 '
        '--docker-images-puppetcentos7@tag latest '
        '--docker-image-pull '
        '--docker-image-stop-timeout 0 '
        'virt.systest.data.suites.test_docker:test_foo_is_mounted_tmpfs ')

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout


@requires(prereq='SkipIfDockerIsNotInstalled')
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
            '--suts-mynode@docker-image puppetcentos7 '
            '--docker-images-ids puppetcentos7 '
            '--docker-images-puppetcentos7@repository docker.zenterio.lan/zenterio/puppet.centos7 '
            '--docker-images-puppetcentos7@tag latest '
            '--docker-images-puppetcentos7@mountpoints type=bind,source={source_path},target=/foo '
            '--docker-image-pull '
            '--docker-image-stop-timeout 0 '
            'virt.systest.data.suites.test_docker:test_foo_is_mounted '
        ).format(source_path=source_path))

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout


@requires(prereq='SkipIfDockerIsNotInstalled')
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
            '--suts-mynode@docker-image puppetcentos7 '
            '--suts-mynode@docker-mountpoints type=bind,source={source_path},target=/foo '
            '--docker-images-ids puppetcentos7 '
            '--docker-images-puppetcentos7@repository docker.zenterio.lan/zenterio/puppet.centos7 '
            '--docker-images-puppetcentos7@tag latest '
            '--docker-image-pull '
            '--docker-image-stop-timeout 0 '
            'virt.systest.data.suites.test_docker:test_foo_is_mounted '
        ).format(source_path=source_path))

    assert 'Passed:  1' in result.stdout
    assert 'Total:   1' in result.stdout
