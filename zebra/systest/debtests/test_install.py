import os


def test_that_zebra_is_installed():
    assert os.path.exists('/opt/venvs/zenterio-zebra/bin/zebra')


def test_that_help_paths_exist(zebra):
    result = zebra('help --print-path --guide ug')

    expected_ug_path = '/opt/venvs/zenterio-zebra/doc/user_guide/html/index.html'
    assert result.stdout.strip() == expected_ug_path, result.stdout
    assert os.path.exists(expected_ug_path)
