import os

from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Path
from zaf.extensions.extension import AbstractExtension, FrameworkExtension

from zpider.asciidoctor import ADOC_FILE, GENERATE_DOC, AsciidoctorCommand
from zpider.data import data_file


class HtmlAsciidoctorCommand(AsciidoctorCommand):

    @property
    def command(self):
        return 'asciidoctor'

    def __init__(self, output_path, css_stylesheet):
        self._output_path = output_path
        self._css_stylesheet = css_stylesheet

    def to_asciidoctor_options(self):
        options = [
            '-b',
            'html5',
            '--attribute',
            'stylesheet={css_stylesheet}'.format(css_stylesheet=self._css_stylesheet),
            '--attribute',
            'toc=left',
            '--attribute',
            'data-uri',  # Embed images directly in the HTML as data URIs
            '--attribute',
            'nofooter',  # Disable the default footer, needed since our own
            # footer would simply be appended to the default footer otherwise
            # and we want to replace it completely.
            '--attribute',
            'docinfo=shared',  # This and the docinfodir attribute is what
            # hooks up our custom docinfo HTML for the header (favicon) and
            # footer (copyright notice).
            '--attribute',
            'docinfodir={htmldocinfo}'.format(htmldocinfo=data_file('docinfo/html')),
        ]
        return ' '.join(options)

    def needed_host_paths(self):
        return [self._css_stylesheet]


def html(zpider):
    adoc_file = os.path.abspath(zpider.config.get(ADOC_FILE))
    output_html = zpider.config.get(OUTPUT_HTML)
    if output_html is None:
        output_html = '{filename}.html'.format(filename=os.path.splitext(adoc_file)[0])
    output_html = os.path.abspath(output_html)

    css_stylesheet = zpider.config.get(HTML_CSS_STYLESHEET)

    futures = zpider.messagebus.send_request(
        GENERATE_DOC, data=HtmlAsciidoctorCommand(output_html, css_stylesheet))
    futures.wait()
    try:
        futures[0].result()
        print('Created output file: {file}'.format(file=output_html))
        return 0
    except Exception as e:
        print("Failed to create file '{file}': {msg}".format(file=output_html, msg=str(e)))
        return 1


OUTPUT_HTML = ConfigOptionId('output.html', 'The output HTML file. Default <input name>.html.')

HTML_CSS_STYLESHEET = ConfigOptionId(
    'css.stylesheet',
    'The CSS stylesheet',
    default=data_file('styles/zenterio-html-theme.css'),
    option_type=Path(exists=True))

HTML_COMMAND = CommandId(
    'html', 'Generate HTML', html, [
        ConfigOption(OUTPUT_HTML, required=False),
        ConfigOption(HTML_CSS_STYLESHEET, required=True),
    ])


@FrameworkExtension(
    name='htmlcommand',
    commands=[HTML_COMMAND],
)
class HtmlCommand(AbstractExtension):
    pass
