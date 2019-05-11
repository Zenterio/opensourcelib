from textwrap import dedent

from ruamel.yaml import YAML
from zaf.component.decorator import component, requires

_SAMPLE_ADOC_DOCUMENT = dedent(
    """
    = Top Level

    [.level]
    == Level Section

    level summary

    level second paragraph

    [.sublevel]
    === Level Subsection

    sublevel summary

    sublevel second paragraph

    ==== Magictitle

    magictitle content

    ==== Other Subsection

    other subsection summary

    other subsection second paragraph
    """)


@component(name='ZpiderYamlBackendAppliedToSampleDocument')
@requires(zpider='Zpider')
@requires(workspace='Workspace')
class ZpiderYamlBackendAppliedToSampleDocument(object):

    def __init__(self, document=_SAMPLE_ADOC_DOCUMENT, zpider=None, workspace=None):
        self._document = document
        self._zpider = zpider
        self._workspace = workspace

    def __call__(self, options=None, expected_exit_code=0):
        yaml_file = self._workspace.absolute_file_path('output.yaml')
        adoc_file = self._workspace.create_file('input.adoc', content=self._document)
        self._zpider(
            (
                'yaml --output-yaml {yaml_file} '
                '--levels-ids level --levels-ids sublevel --magic-titles magictitle '
                '{options} {adoc_file}').format(
                    adoc_file=adoc_file,
                    options=options if options is not None else '',
                    yaml_file=yaml_file),
            expected_exit_code=expected_exit_code)
        yaml = YAML(typ='safe', pure=True)
        with open(yaml_file, 'r') as f:
            return yaml.load(f.read())
