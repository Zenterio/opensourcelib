import os


def test_zit_in_venv():
    assert os.path.exists('.venv/bin/zit')
