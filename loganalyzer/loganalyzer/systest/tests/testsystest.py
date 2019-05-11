import os
import unittest

from ..systest import SysTest


class TestSysTestExec(unittest.TestCase):

    EXEC_OUT = 'exec.out'
    EXEC_PATH = SysTest.build_file(EXEC_OUT)

    def setUp(self):
        super().setUp()
        self.sut = SysTest()

    def tearDown(self):
        if os.path.isfile(self.EXEC_PATH):
            pass
            os.remove(self.EXEC_PATH)
        super().tearDown()

    def test_exec_proc(self):
        self.sut.exec_proc(['env'], self.EXEC_OUT, {'MY_VAR': 'my var'})
        with open(self.EXEC_PATH) as fh:
            env_content = fh.read()
            self.assertTrue(
                'MY_VAR=my var' in env_content,
                'Extended environment did not work:\n{env}'.format(env=env_content))

    def test_exec_shell(self):
        self.sut.exec_shell('env', self.EXEC_OUT, {'MY_VAR': 'my var'})
        with open(self.EXEC_PATH) as fh:
            env_content = fh.read()
            self.assertTrue(
                'MY_VAR=my var' in env_content,
                'Extended environment did not work:\n{env}'.format(env=env_content))

    def test_fail_proc(self):
        self.sut.fail_proc(['ls', 'none-existing-file'], 2, self.EXEC_OUT)
        with open(self.EXEC_PATH) as fh:
            err_content = fh.read()
            self.assertIn('cannot access', err_content)
            self.assertIn('No such file or directory', err_content)

    def test_fail_shell(self):
        self.sut.fail_shell('ls none-existing-file', 2, self.EXEC_OUT)
        with open(self.EXEC_PATH) as fh:
            err_content = fh.read()
            self.assertIn('cannot access', err_content)
            self.assertIn('No such file or directory', err_content)

    def test_filter_out_dependendies(self):

        original_content = """
  File "{base_dir}"/file.py", line 1, foo
  File "{build_dir}/file.py", line 1, foo
  File "some/random/file.py", line 1, foo
  not matching line
  File "{base_dir}"/file.py", line 2, foo
  File "{build_dir}/file.py", line 2, foo
  File "some/random/file.py", line 2, foo
  not matching line
""".format(base_dir=self.sut.BASE_DIR, build_dir=self.sut.BUILD_DIR)

        with open(self.EXEC_PATH, 'wt') as fh:
            fh.write(original_content)

        self.sut.filter_out_path_dependencies(self.EXEC_PATH)

        with open(self.EXEC_PATH) as fh:
            content = fh.read()

        expected = """
  File "BASE_DIR"/file.py", line 1, foo
  File "BUILD_DIR/systest/file.py", line 1, foo
  File EXTERNAL_SOURCE, foo
  not matching line
  File "BASE_DIR"/file.py", line 2, foo
  File "BUILD_DIR/systest/file.py", line 2, foo
  File EXTERNAL_SOURCE, foo
  not matching line
"""
        self.assertEqual(expected, content)


class TestSysTestAsserts(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.sut = SysTest()

    def tearDown(self):
        super().tearDown()

    def test_assertFileExists(self):
        self.sut.assertFileExists(__file__)
        self.assertRaises(Exception, self.sut.assertFileExists, 'invalid file')

    def test_assertFileNotExists(self):
        self.sut.assertFileNotExists('invalid file')
        self.assertRaises(Exception, self.sut.assertFileNotExists, __file__)

    def test_assertFileEmpty(self):
        self.sut.assertFileEmpty(self.sut.data_file('emptyfile'))
        self.assertRaises(Exception, self.sut.assertFileEmpty, __file__)

    def test_assertFileNotEmpty(self):
        self.sut.assertFileNotEmpty(__file__)
        self.assertRaises(Exception, self.sut.assertFileNotEmpty, self.sut.data_file('emptyfile'))
