from zaf.component.decorator import requires


@requires(node='Node')
def test_node(node):
    pass


@requires(exec='Exec', can=('docker', ))
def test_hostname_is_a(exec):
    assert 'a\n' in exec.send_line('hostname -s')


@requires(exec='Exec', can=('docker', ))
def test_hostname_is_b(exec):
    assert 'b\n' in exec.send_line('hostname -s')


@requires(exec='Exec', can=('docker', ))
@requires(infra='Infra', uses=('exec', ))
def test_foo_is_mounted_tmpfs(exec, infra):
    assert infra.mount_point('/foo').exists
    assert 'tmpfs' == infra.mount_point('/foo').filesystem


@requires(exec='Exec', can=('docker', ))
@requires(infra='Infra', uses=('exec', ))
def test_foo_is_mounted(exec, infra):
    assert infra.mount_point('/foo').exists
