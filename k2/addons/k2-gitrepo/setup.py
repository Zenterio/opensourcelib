import os

from setuptools import find_packages, setup

setup(
    name='k2-gitrepo',
    version='0.0.1+' + os.getenv('BUILD_NUMBER', '0'),
    description='Systest component for creating/managing basic git repos',
    long_description=(
        (
            'A systest component for creating and managing git repos, to write tests interacting with git.'
        )),
    maintainer='Zenterio AB',
    maintainer_email='foss@zenterio.com',
    license='Apache 2.0',
    packages=find_packages(
        exclude=[
            '*.test', '*.test.*', 'test.*', 'test', '*.systest', '*.systest.*', 'systest.*',
            'systest'
        ]),
    install_requires=[
        'gitpython<3.0,>=2',
    ],
    entry_points={'k2.addons': ['gitrepo = gitrepo.gitrepo:GitRepoAddon']},
)
