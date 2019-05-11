import subprocess

def test_help():
    subprocess.check_output(['.venv/bin/org_chart_generator', '--help'])
