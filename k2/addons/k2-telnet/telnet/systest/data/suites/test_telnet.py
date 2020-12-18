from zaf.component.decorator import requires


@requires(exec='Exec', can=['telnet'])
def test_telnet_send_hello_world(exec):
    assert 'hello' in exec.send_line('hello', timeout=1)
    assert 'world' in exec.send_line('world', timeout=1)


@requires(exec='Exec', can=['telnet'])
def test_telnet_check_exit_code(exec):
    exec.send_line('true', timeout=1, expected_exit_code=1)
