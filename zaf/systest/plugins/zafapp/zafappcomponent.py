import os
import os.path
import subprocess

from zaf.builtin.logging import LOG_DIR
from zaf.component.decorator import component, requires

zaf_location = subprocess.check_output(['which', 'zaf'], universal_newlines=True).strip()
python3 = os.path.join(os.path.dirname(os.path.realpath(zaf_location)), 'python3')


@component
@requires(python='PyProc', args=(python3, ))
@requires(context='ComponentContext')
@requires(config='Config')
class ZafApp(object):

    def __init__(self, python, context, config):
        self.python = python
        self._context = context
        self._logdir = config.get(LOG_DIR)

    def __call__(
            self,
            enabled_extensions=[],
            command='',
            expected_exit_code=0,
            wait=True,
            file_logging=True,
            application_context='extendable'):

        testapp = '-m systest.data.zafapp.{context}'.format(context=application_context)

        additional_extensions = [
            'click',
            'configurationvalidator',
            'logger',
            'output',
        ]

        file_logging_options = ''
        if file_logging:
            additional_extensions.extend(['filelogger'])
            file_logging_options = (
                "--log-file-ids all --log-file-all@path '${log.dir}/all.log' "
                '--log-file-all@loggers zaf --log-file-all@log-level debug')

        extension_args = ' '.join(
            [
                '--ext-{extension}@enabled true'.format(extension=extension)
                for extension in enabled_extensions + additional_extensions
            ])

        command = (
            '{testapp} '
            '{default_disabled} '
            '{enabled_extensions} '
            '--log-dir {logdir} '
            '{filelogging} '
            '{command}').format(
                testapp=testapp,
                default_disabled=''
                if application_context != 'extendable' else '--ext-default-enabled false',
                enabled_extensions='' if application_context != 'extendable' else extension_args,
                filelogging=file_logging_options,
                command=command,
                logdir=os.path.join(self._logdir, 'tests', self._context.callable_qualname))

        return self.python(command, expected_exit_code=expected_exit_code, wait=wait)
