from zaf.builtin.docgen import GET_CUSTOM_DOC_FILES, GET_CUSTOM_DOCS, DocTemplate
from zaf.builtin.docgen.docgen import DOCGEN_COMMAND
from zaf.extensions.extension import AbstractExtension, CommandExtension
from zaf.messages.decorator import callback_dispatcher


@CommandExtension(name='k2docs', extends=[DOCGEN_COMMAND])
class K2Docs(AbstractExtension):

    package = 'k2.builtin.docgen'

    @callback_dispatcher([GET_CUSTOM_DOCS])
    def get_custom_docs(self, messages):
        templates_dir = 'templates'

        return [
            DocTemplate(K2Docs.package, templates_dir, 'how_to_run.rst'),
            DocTemplate(K2Docs.package, templates_dir, 'workflow.rst'),
            DocTemplate(K2Docs.package, templates_dir, 'docker.rst'),
            DocTemplate(K2Docs.package, templates_dir, 'exec.rst'),
            DocTemplate(K2Docs.package, templates_dir, 'test_cases.rst'),
            DocTemplate(K2Docs.package, templates_dir, 'test_result_reporting.rst'),
        ]

    @callback_dispatcher([GET_CUSTOM_DOC_FILES])
    def get_custom_doc_files(self, message):
        files_dir = 'files'

        return [
            DocTemplate(K2Docs.package, files_dir, 'jenkins_summary.png'),
            DocTemplate(K2Docs.package, files_dir, 'jenkins_failure.png'),
        ]
