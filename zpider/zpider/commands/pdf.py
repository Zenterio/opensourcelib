import os

from zaf.commands.command import CommandId
from zaf.config.options import ConfigOption, ConfigOptionId
from zaf.config.types import Path
from zaf.extensions.extension import AbstractExtension, FrameworkExtension

from zpider.asciidoctor import ADOC_FILE, GENERATE_DOC, AsciidoctorCommand
from zpider.data import data_file


class PdfAsciidoctorCommand(AsciidoctorCommand):

    @property
    def command(self):
        return 'asciidoctor-pdf'

    def __init__(self, output_path, pdf_style_config, pdf_fonts_dir):
        super().__init__(output_path)
        self._pdf_style_config = pdf_style_config
        self._pdf_fonts_dir = pdf_fonts_dir

    def to_asciidoctor_options(self):
        options = [
            '--attribute',
            'pdf-fontsdir={fonts_dir}'.format(fonts_dir=self._pdf_fonts_dir),
            '--attribute',
            'pdf-style={style_config}'.format(style_config=self._pdf_style_config),
            '-d',
            'book',
        ]
        return ' '.join(options)

    def needed_host_paths(self):
        return [self._pdf_style_config, self._pdf_fonts_dir]


def pdf(zpider):
    adoc_file = os.path.abspath(zpider.config.get(ADOC_FILE))
    output_pdf = zpider.config.get(OUTPUT_PDF)
    if output_pdf is None:
        output_pdf = '{filename}.pdf'.format(filename=os.path.splitext(adoc_file)[0])
    output_pdf = os.path.abspath(output_pdf)

    pdf_style = zpider.config.get(PDF_STYLE)
    pdf_fonts = zpider.config.get(PDF_FONTS)

    futures = zpider.messagebus.send_request(
        GENERATE_DOC, data=PdfAsciidoctorCommand(output_pdf, pdf_style, pdf_fonts))
    futures.wait()
    try:
        futures[0].result()
        print('Created output file: {file}'.format(file=output_pdf))
        return 0
    except Exception as e:
        print("Failed to create file '{file}': {msg}".format(file=output_pdf, msg=str(e)))
        return 1


OUTPUT_PDF = ConfigOptionId('output.pdf', 'The output PDF file. Default <input name>.pdf.')

PDF_STYLE = ConfigOptionId(
    'pdf.style',
    'The PDF style configuration',
    default=data_file('styles/zenterio-pdf-theme.yml'),
    option_type=Path(exists=True))

PDF_FONTS = ConfigOptionId(
    'pdf.fonts', 'Directory with fonts', default=data_file('fonts'), option_type=Path(exists=True))

PDF_COMMAND = CommandId(
    'pdf', 'Generate PDF', pdf, [
        ConfigOption(OUTPUT_PDF, required=False),
        ConfigOption(PDF_STYLE, required=True),
        ConfigOption(PDF_FONTS, required=True),
    ])


@FrameworkExtension(
    name='pdfcommand',
    commands=[PDF_COMMAND],
)
class PdfCommand(AbstractExtension):
    pass
