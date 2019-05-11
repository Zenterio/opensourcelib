import os

from setuptools import find_packages, setup

setup(
    name='k2-looper',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Loop test cases, either by runtime or number of loops',
    long_description=(
        (
            'This addon adds the ability to specify how many times or for how long to '
            'execute the tests')),
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
            'looper = looper.looper:Looper',
        ],
    },
)
