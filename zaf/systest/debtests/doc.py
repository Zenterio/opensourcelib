import os

docs = ['user_guide']


def test_that_docs_are_installed():
    for doc in docs:
        assert os.path.exists('/opt/venvs/zenterio-zaf/doc/{doc}/pdf/{doc}.pdf'.format(
            doc=doc)), 'PDF for {doc} was not installed'.format(doc=doc)
        assert os.path.exists('/opt/venvs/zenterio-zaf/doc/{doc}/html/index.html'.format(
            doc=doc)), 'HTML for {doc} was not installed'.format(doc=doc)
