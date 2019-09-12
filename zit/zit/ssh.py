import paramiko


def read_from_ssh(channel):
    buf = b''
    while True:
        c = channel.recv(1)
        buf = buf + c
        if c == b'#':
            return buf.decode('utf-8')


def run_ssh(*commands):
    commands = ['terminal length 0'] + list(commands)
    client = paramiko.client.SSHClient()
    client.load_system_host_keys()
    client.connect(
        'linsw-desk-01.zenterio.lan',
        username='#ENTER_USERNAME_HERE#',
        password='#ENTER_PASSWORD_HERE#',
        allow_agent=False,
        look_for_keys=False)
    result = ''
    channel = client.invoke_shell(term='dumb')
    read_from_ssh(channel)
    for command in commands:
        channel.send(command + '\r')
        command_output = read_from_ssh(channel)
        command_output = command_output[:command_output.rfind('\r\n') + 2]
        command_output = command_output[len(command) + 2:]
        result = result + command_output
    client.close()
    return result
