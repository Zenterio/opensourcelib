import unittest

from zaf.builtin.unittest.harness import ExtensionTestHarness

from ..systestutils import SystestUtils


class TestSystestUtils(unittest.TestCase):

    def test_systest_utils_extension_can_be_initialized(self):
        with create_harness():
            pass


def create_harness():
    return ExtensionTestHarness(SystestUtils, )
