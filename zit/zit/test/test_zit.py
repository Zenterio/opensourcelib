import unittest

from ..__main__ import do


class TestZit(unittest.TestCase):

    def test_main(self):
        do()
