import os

from setuptools import find_packages, setup

setup(
    name='k2-zelenium',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Selenium support for K2',
    long_description=(
        'Selenium is a browser automation framework that can be used to test web services.'),
    maintainer='Zenterio AB',
    maintainer_email='foss@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[
        'selenium<4.0,>=3',
    ],
    entry_points={
        'k2.addons': [
            'zelenium = zelenium.zelenium:Zelenium',
        ],
    },
    package_data={'zelenium': ['bin/*']},
)
