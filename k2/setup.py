try:
    import fastentrypoints
except ImportError as e:
    pass
from setuptools import find_packages, setup

from k2 import __version__

setup(
    name='zenterio-zk2',

    version=__version__,

    description='Zenterio K2 automated asynchronous test framework',
    long_description='Zenterio K2 is an automated asynchronous test framework for testing Zenterio STBs',

    maintainer='Zenterio AB',
    maintainer_email='foss@zenterio.com',

    license='Apache 2.0',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Test Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='test automation',

    packages=find_packages(exclude=['*.test', '*.test.*', 'test.*', 'systest', 'systest.*', 'example', 'example.*']),

    install_requires=[
        'nose<2.0,>=1',
        'pytracing<1.0,>=0',
        'requests<3.0,>=2',
        'zenterio-zaf<2.0',
        'junit-xml<2.0,>=1.8',
    ],

    entry_points={
        'console_scripts': [
            'zk2 = k2.__main__:main',
        ],
        'k2.addons': [
            'signalhandler = k2.signal.signalhandler:SignalHandler',

            'sut = k2.sut.sut:Sut',

            'testfinder = k2.finder.testfinder:TestFinder',
            'testrunner = k2.runner.manager:TestRunnerManager',
            'testscheduler = k2.scheduler.scheduler:TestScheduler',

            'testresults = k2.results.results:TestResults',
            'testcasetimeout = k2.runner.timeout:TestCaseTimeout',

            'junitreport = k2.reports.junit.junit:JUnitReporter',
            'testngreport = k2.reports.testng.testng:TestNgReporter',
            'textreport = k2.reports.text.text:TextReporter',
            'z2reportgenerator = k2.reports.z2.z2:ReportGenerator',
            'z2filereporter = k2.reports.z2.z2:FileReporter',
            'z2uploadreporter = k2.reports.z2.z2:UploadReporter',

            'listcommand = k2.cmd.list:ListCommand',
            'runcommand = k2.cmd.run:RunCommand',
            'noop = k2.cmd.noop:NoopCommand',

            'abortonfail = k2.builtin.aborttestrun.abortonfail:AbortOnFail',
            'abortonunexpectedsutreset = k2.builtin.aborttestrun.abortonsutreset:AbortOnUnexpectedSutReset',

            'systestutils = k2.builtin.systestutils.systestutils:SystestUtils',
            'proc = k2.builtin.proc.proc:Proc',
            'pyproc = k2.builtin.proc.pyproc:PyProcExtension',
            'commandtimeout = k2.builtin.commandtimeout.commandtimeout:CommandTimeout',
            'logdefaults = k2.builtin.logdefaults.logdefaults:LogDefaults',
            'logdefaultsdocs = k2.builtin.logdefaults.logdefaults:LogDefaultsDocs',
            'waitfor = k2.builtin.waitfor.common:WaitFor',
            'k2docs = k2.builtin.docgen.docgen:K2Docs',
        ]
    },

    package_data={
        'k2.builtin.docgen': ['templates/*.rst', 'files/*.*'],
        'k2.builtin.logdefaults': ['templates/*.rst'],
    },
)
