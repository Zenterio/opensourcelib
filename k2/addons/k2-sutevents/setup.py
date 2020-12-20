import os

from setuptools import find_packages, setup

setup(
    name='k2-sutevents',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='SUT Event definitions',
    long_description=('Common event definition describing events on the SUT.'),
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
            'suteventscomponents = sutevents.components:SutEventsComponentExtension',
            'suteventslog = sutevents.suteventslog:SutEventsLogExtension',
            'suteventstime = sutevents.suteventstime:SutEventsTimeExtension',
        ],
    },
)
