import unittest

from zaf.extensions.extension import FrameworkExtension
from zaf.extensions.manager import ExtensionManager

from ..packages import NoSuchExtension, find_packages

THIS_PACKAGE = __name__.rsplit('.', 1)[0]


class TestFindPackages(unittest.TestCase):

    def setUp(self):
        self.em = ExtensionManager()
        self.em.add_extension(extA1)
        self.em.add_extension(extA2)
        self.em.add_extension(extB1)
        self.em.enable_all_extensions()

    def test_find_packages_for_single_extension(self):
        self.assertCountEqual(find_packages(['extb'], self.em, 'name', 'package'), ['addons'])

    def test_find_packages_for_two_extensions_with_same_name(self):
        self.assertCountEqual(
            find_packages(['exta'], self.em, 'name', 'package'), [THIS_PACKAGE, 'addons.package'])

    def test_find_packages_for_core(self):
        self.assertCountEqual(find_packages(['name'], self.em, 'name', 'package'), ['package'])

    def test_find_packages_merges_packages(self):
        self.assertCountEqual(
            find_packages(['exta', 'extb'], self.em, 'name', 'package'), [THIS_PACKAGE, 'addons'])

    def test_find_packages_for_all_extensions(self):
        self.assertCountEqual(find_packages([], self.em, 'zaf', 'zaf'), ['addons', 'zaf'])

    def test_find_packages_with_invalid_extension_name_raises_exception(self):
        self.assertRaises(
            NoSuchExtension, find_packages, ['NO_SUCH_EXTENSION'], self.em, 'name', 'package')


@FrameworkExtension(name='exta')
class extA1():
    __module__ = 'addons.package.exta1_module'
    pass


@FrameworkExtension(name='exta')
class extA2():
    pass


@FrameworkExtension(name='extb')
class extB1():
    __module__ = 'addons.extb1_module'
    pass
