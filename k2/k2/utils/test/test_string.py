from unittest import TestCase

from ..string import strip_ansi_escapes


class TestStripAnsiEscapes(TestCase):

    def test_strips_colors(self):
        self.assertEqual(strip_ansi_escapes('\x1b[31mClean\x1b[0m'), 'Clean')

    def test_strips_cursor_movements(self):
        self.assertEqual(strip_ansi_escapes('\x1b[3AClean\x1b[4;4H'), 'Clean')
