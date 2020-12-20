import os

from setuptools import find_packages, setup

setup(
    name='k2-telnet',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Telnet support for K2',
    long_description=('Allows K2 to use telnet to connect to and execute commands on SUT.'),
    maintainer='Zenterio AB',
    maintainer_email='foss@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[
        'pexpect<5.0,>=4',
    ],
    entry_points={
        'k2.addons': [
            'telnet = telnet.telnet:Telnet',
            'telnetcc = telnet.telnetcc:TelnetConnectionCheck',
        ],
    },
)
