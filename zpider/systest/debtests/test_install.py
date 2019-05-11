import os


def test_that_zpider_is_installed():
    assert os.path.exists('/opt/venvs/zenterio-zpider/bin/zpider')


def test_that_document_is_included(zpider):
    assert os.path.exists('/opt/venvs/zenterio-zpider/doc/user_guide/html/index.html')
    assert os.path.exists('/opt/venvs/zenterio-zpider/doc/user_guide/pdf/user_guide.pdf')
