import os

from zaf.component.decorator import requires


@requires(zpider='Zpider')
@requires(workspace='Workspace')
@requires(data='Data')
def test_generate_html_from_simple_adoc_file(zpider, workspace, data):
    dir = workspace.path

    workspace.add_file(data.file('simple.adoc'), 'simple.adoc')
    zpider('html --output-html output.html simple.adoc', cwd=dir)
    workspace.assert_file_exists('output.html')


@requires(zpider='Zpider')
@requires(workspace='Workspace')
@requires(data='Data')
def test_default_html_output_name_is_same_as_input_adoc_file(zpider, workspace, data):
    dir = workspace.path

    workspace.add_file(data.file('simple.adoc'), 'simple.adoc')
    zpider('html simple.adoc', cwd=dir)
    workspace.assert_file_exists('simple.html')


@requires(zpider='Zpider')
@requires(workspace='Workspace')
@requires(data='Data')
def test_generating_html_output_file_outside_of_current_working_directory(zpider, workspace, data):
    dir = workspace.path
    cwd = os.path.join(dir, 'cwd')

    workspace.add_file(data.file('simple.adoc'), 'cwd/simple.adoc')
    zpider('html --output-html {dir}/output.html simple.adoc'.format(dir=dir), cwd=cwd)
    workspace.assert_file_exists('output.html')


@requires(zpider='Zpider')
@requires(workspace='Workspace')
@requires(data='Data')
def test_generating_html_output_file_containing_images_and_diagrams(zpider, workspace, data):
    dir = workspace.path
    cwd = os.path.join(dir, 'cwd')

    workspace.add_file(data.file('diagrams_and_images.adoc'), 'cwd/diagrams_and_images.adoc')
    workspace.add_file(data.file('assets/zpider.png'), 'cwd/assets/zpider.png')
    workspace.add_file(data.file('plantUML/diagram.uml'), 'cwd/plantUML/diagram.uml')

    zpider('html --output-html {dir}/output.html diagrams_and_images.adoc'.format(dir=dir), cwd=cwd)
    workspace.assert_file_exists('output.html')
