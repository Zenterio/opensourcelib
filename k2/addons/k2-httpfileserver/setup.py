import os

from setuptools import find_packages, setup

setup(
    name='k2-httpfileserver',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='K2 HTTP File-Server',
    long_description=('Simple HTTP server for serving static files.'),
    maintainer='Zenterio AB',
    maintainer_email='foss@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[
        'requests<3.0,>=2',
    ],
    entry_points={
        'k2.addons': [
            'httpfileserver = httpfileserver.httpfileserver:HttpFileServerAddon',
        ],
    },
)
