import os

from setuptools import find_packages, setup

setup(
    name='k2-upgrade',
    version='0.0.1' + os.getenv('BUILD_NUMBER', '0'),
    description='Upgrade SUT software',
    long_description=('Interface addon for upgrading software on a SUT'),
    maintainer='Patrik Dahlström',
    maintainer_email='risca@dalakolonin.se',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[''],
    entry_points={
        'k2.addons': [
            'upgradecommand = upgrade.upgradecommand:UpgradeExtension',
        ],
    },
)
