from zaf.config.options import ConfigOptionId

HOST_SHELL_EXEC_ENABLED = ConfigOptionId(
    'host.shell.exec.enabled', 'Enable the host shell exec addon.', option_type=bool, default=False)

HOST_SHELL_EXEC_TIMEOUT = ConfigOptionId(
    'host.shell.exec.timeout',
    'Default timeout when waiting for a command to complete',
    option_type=int,
    default=60)

HOST_SHELL_EXEC_ENCODING = ConfigOptionId(
    'host.shell.exec.encoding',
    'Encoding to use when reading data from the host shell',
    option_type=str,
    default='utf-8')
