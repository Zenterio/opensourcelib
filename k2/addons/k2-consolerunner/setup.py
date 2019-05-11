import os

from setuptools import find_packages, setup

setup(
    name='k2-consolerunner',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Runs commands and parses the console output.',
    maintainer='Zenterio AB',
    maintainer_email='engineering.services@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[],
    entry_points={
        'k2.addons': [
            'consolerunner = consolerunner.consolerunner:ConsoleRunner',
        ],
    },
)
