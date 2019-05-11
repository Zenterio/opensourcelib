import os

from zaf.component.decorator import requires


@requires(zpider='Zpider')
@requires(workspace='Workspace')
@requires(data='Data')
def test_generate_yaml_from_simple_adoc_file(zpider, workspace, data):
    dir = workspace.path

    workspace.add_file(data.file('simple.adoc'), 'simple.adoc')
    zpider('yaml --output-yaml simple.yaml simple.adoc', cwd=dir)
    workspace.assert_file_exists('simple.yaml')


@requires(zpider='Zpider')
@requires(workspace='Workspace')
@requires(data='Data')
def test_default_yaml_output_name_is_same_as_input_adoc_file(zpider, workspace, data):
    dir = workspace.path

    workspace.add_file(data.file('simple.adoc'), 'simple.adoc')
    zpider('yaml simple.adoc', cwd=dir)
    workspace.assert_file_exists('simple.yaml')


@requires(zpider='Zpider')
@requires(workspace='Workspace')
@requires(data='Data')
def test_generating_yaml_output_file_outside_of_current_working_directory(zpider, workspace, data):
    dir = workspace.path
    cwd = os.path.join(dir, 'cwd')

    workspace.add_file(data.file('simple.adoc'), 'cwd/simple.adoc')
    zpider('yaml --output-yaml {dir}/output.yaml simple.adoc'.format(dir=dir), cwd=cwd)
    workspace.assert_file_exists('output.yaml')
