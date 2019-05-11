import os

from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.extensions.extension import AbstractExtension, FrameworkExtension

from zpider.asciidoctor import ADOC_FILE, GENERATE_DOC, AsciidoctorCommand


class YamlAsciidoctorCommand(AsciidoctorCommand):

    @property
    def command(self):
        return 'asciidoctor'

    def __init__(self, output_path):
        super().__init__(output_path)

    def to_asciidoctor_options(self):
        options = ['-b', 'yaml']
        return ' '.join(options)


def yaml(zpider):
    adoc_file = os.path.abspath(zpider.config.get(ADOC_FILE))
    output_yaml = zpider.config.get(OUTPUT_YAML)
    if output_yaml is None:
        output_yaml = '{filename}.yaml'.format(filename=os.path.splitext(adoc_file)[0])
    output_yaml = os.path.abspath(output_yaml)

    futures = zpider.messagebus.send_request(GENERATE_DOC, data=YamlAsciidoctorCommand(output_yaml))
    futures.wait()
    try:
        futures[0].result()
        print('Created output file: {file}'.format(file=output_yaml))
        return 0
    except Exception as e:
        print("Failed to create file '{file}': {msg}".format(file=output_yaml, msg=str(e)))
        return 1


OUTPUT_YAML = ConfigOptionId('output.yaml', 'The output YAML file. Default <input name>.yaml.')

YAML_COMMAND = CommandId(
    'yaml', 'Generate YAML', yaml, [
        ConfigOption(OUTPUT_YAML, required=False),
    ])


@FrameworkExtension(
    name='yamlcommand',
    commands=[YAML_COMMAND],
)
class YamlCommand(AbstractExtension):
    pass
