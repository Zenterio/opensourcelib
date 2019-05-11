from tempfile import NamedTemporaryFile
from unittest import TestCase

from debpacker.common.preparedassets import OutputExists, prepared_output_file


class TestPrepareOutputFile(TestCase):

    def test_prepare_no_output_file(self):
        # assert no exceptions
        prepared_output_file('')
        prepared_output_file(None)

    def test_prepare_existing_output_file(self):
        with NamedTemporaryFile() as test_file:
            with self.assertRaises(OutputExists):
                prepared_output_file(test_file.name)

    def test_prepare_existing_output_file_with_force(self):
        with NamedTemporaryFile() as test_file:
            # assert no exception
            prepared_output_file(test_file.name, True)
