import os

from setuptools import find_packages, setup

setup(
    name='k2-gtestbinaryrunner',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='K2 GTest runner',
    long_description=('Run GTest binaries on SUT.'),
    maintainer='Zenterio AB',
    maintainer_email='foss@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[''],
    entry_points={
        'k2.addons': [
            'gtestbinaryrunner = gtestbinaryrunner.gtestbinaryrunner:GtestBinaryRunner',
        ],
    },
)
