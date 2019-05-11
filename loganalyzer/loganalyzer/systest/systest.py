import os
import re
import subprocess
import unittest


class SysTest(unittest.TestCase):

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    PACKAGE_DIR = os.path.join(BASE_DIR, 'loganalyzer')
    BUILD_DIR = os.path.join(
        os.environ.get('LOG_ANALYZER_BUILD_BASE', BASE_DIR), 'build', 'systest')
    TEST_DIR = os.path.join(PACKAGE_DIR, 'systest')
    RESOURCE_DIR = os.path.join(TEST_DIR, 'resources')
    BASELINE_DIR = os.path.join(RESOURCE_DIR, 'baseline')
    CONFIG_DIR = os.path.join(RESOURCE_DIR, 'config')
    DATA_DIR = os.path.join(RESOURCE_DIR, 'data')
    BIN_DIR = os.path.join(os.environ.get('LOG_ANALYZER_INSTALLATION', BASE_DIR), 'bin')

    _TEMP_OUT = 'temp.out'
    _RE_EXTERNAL_SOURCE = re.compile(
        '(?<=File )("(?!BASE_DIR|BUILD_DIR).*line [0-9]+)(?=, )', flags=re.MULTILINE)
    _RE_PYTHON34_TO_PYTHON35_REGEX_ERROR_MESSAGE_COMPATIBILITY = \
        re.compile(r"unbalanced parenthesis: '.*?'|missing \), unterminated subpattern at position [0-9]+: '.*?'")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        super().setUp()

    def tearDown(self):
        temp = self.build_file(self._TEMP_OUT)
        if os.path.exists(temp):
            os.remove(temp)
        super().tearDown()

    def exec_proc(self, proc_cmd, outfile=_TEMP_OUT, extenv={}, cwd=None):
        env = dict(os.environ.copy())
        env.update(extenv)
        with open(self.build_file(outfile), 'wb') as out:
            ph = subprocess.Popen(proc_cmd, stdout=out, stderr=subprocess.PIPE, env=env, cwd=cwd)
            dummy, err = ph.communicate()
            msg = 'Execution failed: \n' + ' '.join(proc_cmd) + '\n' + err.decode('utf-8')
        self.filter_out_path_dependencies(self.build_file(outfile))
        self.assertEqual(0, ph.returncode, msg)

    def fail_proc(self, proc_cmd, exit_code=0, outfile=_TEMP_OUT, extenv={}, cwd=None):
        env = dict(os.environ.copy())
        env.update(extenv)
        with open(self.build_file(outfile), 'wb') as err:
            ph = subprocess.Popen(proc_cmd, stdout=subprocess.PIPE, stderr=err, env=env, cwd=cwd)
            out, _ = ph.communicate()
            msg = 'Execution should exit with code {expected_code} ' \
                  'but was {result_code}: \n ' \
                  '{cmdline}\n {out}'.format(expected_code=exit_code,
                                             result_code=ph.returncode,
                                             cmdline=' '.join(proc_cmd),
                                             out=out.decode('utf-8'))

        self.filter_out_path_dependencies(self.build_file(outfile))
        self.assertEqual(exit_code, ph.returncode, msg)

    def exec_shell(self, cmdline, outfile=_TEMP_OUT, extenv={}, cwd=None):
        env = dict(os.environ.copy())
        env.update(extenv)
        with open(self.build_file(outfile), 'wb') as out:
            ph = subprocess.Popen(
                cmdline, shell=True, stdout=out, stderr=subprocess.PIPE, env=env, cwd=cwd)
            _, err = ph.communicate()
            msg = 'Execution failed: \n ' + cmdline + '\n' + err.decode('utf-8')
        self.filter_out_path_dependencies(self.build_file(outfile))
        self.assertEqual(0, ph.returncode, msg)

    def fail_shell(self, cmdline, exit_code=0, outfile=_TEMP_OUT, extenv={}, cwd=None):
        env = dict(os.environ.copy())
        env.update(extenv)
        with open(self.build_file(outfile), 'wb') as err:
            ph = subprocess.Popen(
                cmdline, shell=True, stdout=subprocess.PIPE, stderr=err, env=env, cwd=cwd)
            out, _ = ph.communicate()
            msg = 'Execution should exit with code {expected_code} ' \
                  'but was {result_code}: \n ' \
                  '{cmdline}\n {out}'.format(expected_code=exit_code,
                                             result_code=ph.returncode,
                                             cmdline=cmdline,
                                             out=out.decode('utf-8'))
        self.filter_out_path_dependencies(self.build_file(outfile))
        self.assertEqual(exit_code, ph.returncode, msg)

    def baseline_check(self, outfile):
        ph = subprocess.Popen(
            ['git', 'diff', '--no-index',
             self.baseline_file(outfile),
             self.build_file(outfile)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = ph.communicate()
        msg = 'Baseline check failed: ' + outfile
        msg += '\n' + stdout.decode('utf-8') + '\n' + stderr.decode('utf-8')
        self.assertEqual(0, ph.returncode, msg)

    def exec_proc_and_baseline_check(self, proc_cmd, outfile, extenv={}, cwd=None):
        self.exec_proc(proc_cmd, outfile, extenv, cwd)
        self.baseline_check(outfile)

    def assertFileExists(self, path):
        self.assertTrue(os.path.exists(path), 'File does not exist (path={path})'.format(path=path))

    def assertFileNotExists(self, path):
        self.assertFalse(os.path.exists(path), 'File exist (path={path})'.format(path=path))

    def assertFileEmpty(self, path):
        self.assertFileExists(path)
        self.assertEqual(0, os.path.getsize(path), 'File does not hot have zero size.')

    def assertFileNotEmpty(self, path):
        self.assertFileExists(path)
        self.assertGreater(os.path.getsize(path), 0, 'File size not greater than zero.')

    def assertFileContains(self, path, *content):
        with open(path) as fh:
            file_content = fh.read()

        for snippet in content:
            msg = ('Snippet could not be find in file\'s content '
                   '(snippet={snip}, path={path})').format(
                       snip=snippet, path=path)
            self.assertTrue(snippet in file_content, msg)

    @classmethod
    def filter_out_path_dependencies(cls, path):

        with open(path) as fh:
            file_content = fh.read()

        file_content = file_content.replace(cls.BUILD_DIR, 'BUILD_DIR/systest')
        file_content = file_content.replace(cls.BASE_DIR, 'BASE_DIR')
        file_content = cls._RE_EXTERNAL_SOURCE.sub('EXTERNAL_SOURCE', file_content)
        file_content = cls._RE_PYTHON34_TO_PYTHON35_REGEX_ERROR_MESSAGE_COMPATIBILITY\
            .sub('REGEXP_ERROR_MESSAGE', file_content)

        with open(path, 'wt') as fh:
            fh.write(file_content)

    @classmethod
    def build_file(cls, path):
        return os.path.abspath(os.path.join(cls.BUILD_DIR, path))

    @classmethod
    def baseline_file(cls, path):
        return os.path.abspath(os.path.join(cls.BASELINE_DIR, path))

    @classmethod
    def config_file(cls, path):
        return os.path.abspath(os.path.join(cls.CONFIG_DIR, path))

    @classmethod
    def data_file(cls, path):
        return os.path.abspath(os.path.join(cls.DATA_DIR, path))


os.makedirs(SysTest.BUILD_DIR, exist_ok=True)
