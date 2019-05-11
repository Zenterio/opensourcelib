import subprocess

def test_help():
    subprocess.check_output(['.venv/bin/docs_fetcher', '--help'])
