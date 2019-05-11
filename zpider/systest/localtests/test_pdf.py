import os

from zaf.component.decorator import requires


@requires(zpider='Zpider')
@requires(workspace='Workspace')
@requires(data='Data')
def test_generate_pdf_from_simple_adoc_file(zpider, workspace, data):
    dir = workspace.path

    workspace.add_file(data.file('simple.adoc'), 'simple.adoc')
    zpider('pdf --output-pdf simple.pdf simple.adoc', cwd=dir)
    workspace.assert_file_exists('simple.pdf')


@requires(zpider='Zpider')
@requires(workspace='Workspace')
@requires(data='Data')
def test_default_pdf_output_name_is_same_as_input_adoc_file(zpider, workspace, data):
    dir = workspace.path

    workspace.add_file(data.file('simple.adoc'), 'simple.adoc')
    zpider('pdf simple.adoc', cwd=dir)
    workspace.assert_file_exists('simple.pdf')


@requires(zpider='Zpider')
@requires(workspace='Workspace')
@requires(data='Data')
def test_generating_pdf_output_file_outside_of_current_working_directory(zpider, workspace, data):
    dir = workspace.path
    cwd = os.path.join(dir, 'cwd')

    workspace.add_file(data.file('simple.adoc'), 'cwd/simple.adoc')
    zpider('pdf --output-pdf {dir}/output.pdf simple.adoc'.format(dir=dir), cwd=cwd)
    workspace.assert_file_exists('output.pdf')


@requires(zpider='Zpider')
@requires(workspace='Workspace')
@requires(data='Data')
def test_generating_pdf_output_file_containing_images_and_diagrams(zpider, workspace, data):
    dir = workspace.path
    cwd = os.path.join(dir, 'cwd')

    workspace.add_file(data.file('diagrams_and_images.adoc'), 'cwd/diagrams_and_images.adoc')
    workspace.add_file(data.file('assets/zpider.png'), 'cwd/assets/zpider.png')
    workspace.add_file(data.file('plantUML/diagram.uml'), 'cwd/plantUML/diagram.uml')

    zpider('pdf --output-pdf {dir}/output.pdf diagrams_and_images.adoc'.format(dir=dir), cwd=cwd)
    workspace.assert_file_exists('output.pdf')
