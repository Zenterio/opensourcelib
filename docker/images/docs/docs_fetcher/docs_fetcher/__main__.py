import collections
import io
import logging
import os
import re
import shutil
import tarfile
import time

import artifactory
import click
import urllib3

urllib3.disable_warnings()

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def get_artifactory_repository(url):
    return artifactory.ArtifactoryPath(url, verify=False)


def create_docs_directory(docs_directory):
    try:
        logger.info('Removing docs directory: {directory}'.format(directory=docs_directory))
        shutil.rmtree(docs_directory)
    except FileNotFoundError:
        pass
    logger.info('Creating docs directory: {directory}'.format(directory=docs_directory))
    os.mkdir(docs_directory)


def fetch_and_extract_docs_archive(documentation_archive, docs_directory):
    try:
        logger.info(
            'Fetching documentation archive: {documentation_archive}'.format(
                documentation_archive=documentation_archive))
        archive = tarfile.open(fileobj=io.BytesIO(documentation_archive.path.open().read()))
    except Exception:
        logger.error(
            'Could not fetch documentation archive: {documentation_archive}'.format(
                documentation_archive=documentation_archive))

    try:
        logger.info(
            'Extracting documentation archive: {documentation_archive}'.format(
                documentation_archive=documentation_archive))
        archive.extractall(path=os.path.join(docs_directory, documentation_archive.module))
    except Exception:
        logger.error(
            'Could not extract documentation archive: {documentation_archive}'.format(
                documentation_archive=documentation_archive))


class DocumentationArchive(object):

    def __init__(self, module, name, version):
        self.module = module
        self.name = name
        self.version = version
        self.path = None
        self.fetched = False

    @property
    def key(self):
        return (self.module, self.name)

    @classmethod
    def from_dict(cls, data):
        return cls(data['module'], data['name'], data['version'])

    def __str__(self):
        return self.module + '/' + self.name + ' (' + self.version + ')'


def keep_docs_directory_up_to_date(repository, docs_directory, delay):
    documentation_archives = collections.defaultdict(lambda: None)
    documentation_archive_pattern = re.compile(
        r'.*/(?P<module>[^/]+)/(?P<name>.*)-(?P<version>\d+).tar.gz')

    logger.info('Starting keeping docs directory up to date')
    while True:
        try:
            for path in repository.glob('**/*.tar.gz'):
                match = documentation_archive_pattern.match(str(path))
                if not match:
                    continue
                candidate_archive = DocumentationArchive.from_dict(match.groupdict())
                candidate_archive.path = path
                current_archive = documentation_archives[candidate_archive.key]
                if current_archive is None or int(current_archive.version) < int(
                        candidate_archive.version):
                    documentation_archives[candidate_archive.key] = candidate_archive
            for documentation_archive in documentation_archives.values():
                if documentation_archive.fetched is False:
                    fetch_and_extract_docs_archive(documentation_archive, docs_directory)
                    documentation_archive.fetched = True
        except Exception as e:
            logger.error(str(e))
        finally:
            time.sleep(delay)
    logger.info('Terminating')


@click.command()
@click.option(
    '--artifactory-url',
    default='URL TO YOUR ARTIFACTORY',
    help='URL for the docs Artifactory repository.')
@click.option(
    '--docs-directory', default='/usr/local/apache2/htdocs/', help='Path to write documentation to')
@click.option('--delay', default=120, help='Seconds between checking for updated documentation')
def main(artifactory_url, docs_directory, delay):
    logging.basicConfig(level=logging.INFO)
    repository = get_artifactory_repository(artifactory_url)
    create_docs_directory(docs_directory)
    keep_docs_directory_up_to_date(repository, docs_directory, delay)


if __name__ == '__main__':
    main()
