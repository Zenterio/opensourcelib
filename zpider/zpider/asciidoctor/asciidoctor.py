import logging
import os
import shutil
import tempfile
from datetime import datetime

from zaf.component.decorator import requires
from zaf.config.options import ConfigOption
from zaf.extensions.extension import AbstractExtension, CommandExtension, get_logger_name
from zaf.messages.decorator import callback_dispatcher

from zpider.asciidoctor import ADOC_FILE, ASCIIDOCTOR_ENDPOINT, GENERATE_DOC, \
    GET_ASCIIDOCTOR_OPTIONS, GenerateDocException
from zpider.commands.html import HTML_COMMAND
from zpider.commands.pdf import PDF_COMMAND
from zpider.commands.yaml import YAML_COMMAND
from zpider.data import data_file
from zpider.environments import RunException

logger = logging.getLogger(get_logger_name('zpider', 'asciidoctor'))
logger.addHandler(logging.NullHandler())


@CommandExtension(
    name='asciidoctor',
    extends=[HTML_COMMAND, PDF_COMMAND, YAML_COMMAND],
    config_options=[
        ConfigOption(ADOC_FILE, required=True),
    ],
    endpoints_and_messages={
        ASCIIDOCTOR_ENDPOINT: [GENERATE_DOC],
    },
)
class AsciidoctorExtension(AbstractExtension):

    def __init__(self, config, instances):
        self._adoc_file = config.get(ADOC_FILE)

    @callback_dispatcher([GENERATE_DOC], [ASCIIDOCTOR_ENDPOINT])
    @requires(env='Env')
    @requires(messagebus='MessageBus')
    def generate_doc(self, message, env, messagebus):
        command = message.data

        try:
            with tempfile.TemporaryDirectory() as dir:
                temp_output_path = os.path.join(dir, os.path.basename(command.output_path))

                assets_path = os.path.join(os.getcwd(), 'assets')
                temp_images_path = os.path.join(os.path.dirname(temp_output_path), 'images')
                if os.path.exists(assets_path):
                    shutil.copytree(assets_path, os.path.join(temp_images_path, 'assets'))

                host_paths = [os.path.dirname(temp_output_path)]
                host_paths.extend(command.needed_host_paths())

                env.run(
                    '{command} {options} {additional_options} {output_options} {adoc_file}'.format(
                        command=command.command,
                        adoc_file=self._adoc_file,
                        options=self._get_options(temp_images_path, temp_output_path),
                        additional_options=self._get_additional_options(messagebus),
                        output_options=command.to_asciidoctor_options(),
                    ),
                    host_paths=host_paths)

                os.makedirs(os.path.dirname(command.output_path), exist_ok=True)
                shutil.copy(temp_output_path, command.output_path)
        except RunException:
            raise GenerateDocException('Asciidoctor command failed')

    def _get_options(self, images_dir, output_path):
        options = [
            '--attribute',
            'chapter-label',
            '--attribute',
            'pagenums',
            '--attribute',
            'title-logo-image=image:{title_logo}[]'.format(
                title_logo=data_file('logos/zenterio-title-logo.png')),
            '--attribute',
            'toc',
            '--attribute',
            'sectnums',
            '--attribute',
            'sectnumlevels=5',
            '--attribute',
            'xrefstyle=full',
            '--attribute',
            'localyear={year}'.format(year=datetime.now().year),
            '--attribute',
            'source-highlighter=coderay',
            '--base-dir',
            '.',
            '--source-dir',
            '.',
            '--trace',
            '--attribute',
            'imagesdir={imagesdir}'.format(imagesdir=images_dir),
            '--attribute',
            'imagesoutdir={imagesoutdir}'.format(imagesoutdir=images_dir),
        ]

        # This might be modified if to support for output directories is needed
        options.extend(['--out-file', output_path])

        return ' '.join(options)

    def _get_additional_options(self, messagebus):
        futures = messagebus.send_request(GET_ASCIIDOCTOR_OPTIONS)
        return ' '.join([future.result() for future in futures.as_completed()])
