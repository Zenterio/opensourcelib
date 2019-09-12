import os


def test_zit_is_installed():
    assert os.path.exists('/opt/venvs/zenterio-zit/bin/zit')
