
import os
import subprocess
from textwrap import dedent

from zaf.component.decorator import requires


@requires(workspace='Workspace')
def test_generate_from_default_template(workspace):
    input_file = workspace.create_file('orgchart.csv', dedent("""
        VD,Nisse,Exec Team,Nisse VD
        Kilbrand,Olle,R&D,Nisse VD
        Nilsson,Andreas,Engineering Services,Olle Kilbrand
        """))

    output_file = os.path.join(workspace.path, 'index.html')
    subprocess.check_output(['.venv/bin/org_chart_generator',
                             '--update-interval', '0', '--output', output_file, input_file])

    with open(output_file, 'r') as f:
        resulting_html = f.read()

        assert 'Nisse VD' in resulting_html, resulting_html
        assert 'Olle Kilbrand' in resulting_html, resulting_html
        assert 'Andreas Nilsson' in resulting_html, resulting_html
