from os.path import dirname, realpath, join, basename, splitext
import glob
import pytest

test_dir = join(dirname(dirname(realpath(__file__))), 'test')
test_files = list(map(basename, glob.glob(test_dir + "/*.test")))
suite_list = list(map(lambda f: splitext(f)[0], test_files))
suite_list.sort()


@pytest.mark.parametrize("suite", suite_list)
def test_unit_test_on_system(Command, suite):
    Command.run_expect([0], 'make -C /vagrant/ test SYSTEM_TEST=y TEST_FILTER="{suite}"'.format(suite=suite))
