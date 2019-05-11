import gzip
import logging
from io import BytesIO

import requests
import yaml

logger = logging.getLogger(__name__)

package_list_url_pattern = 'http://deb.zenterio.lan/apt/debian/dists/{dist}/main/binary-amd64/Packages.gz'
package_list_urls = {
    'xenial': package_list_url_pattern.format(dist='xenial'),
    'trusty': package_list_url_pattern.format(dist='trusty'),
    'bionic': package_list_url_pattern.format(dist='bionic'),
}


def retrieve_package_version_mapping(package_list_urls=package_list_urls) -> {str: {str: str}}:
    """
    Retrieves a dict from package to version for each dist in package_list_urls.
    :param package_list_urls: dict from dist to an URL to a package list
    :return: dict from package name and version divided by distribution
             {dist: {name: version}}
    """
    package_versions = {}

    for dist, package_list in retrieve_package_lists(package_list_urls).items():
        dist_packages = {}
        package_versions[dist] = dist_packages
        for package in package_list:
            name = package['Package']
            version = package['Version']

            dist_packages[name] = version

    return package_versions


def retrieve_package_lists(package_list_urls=package_list_urls, filter_dist=None) -> {
        str: [{str, str}]
}:
    """
    Retrieving the package list for each dist in package_list_urls or for a single dist.
    The result is not filtered for duplicates.
    :param package_list_urls: map from dist to url to the Packages.gz file
    :param filter_dist: if not None only the specified dist will be used.
    :return: dict from dist to list of packages with the keys and values from the Packages.gz file
             {dist: [{key: value}]}
    """
    package_lists = {}
    for dist, url in package_list_urls.items():
        if filter_dist is None or dist == filter_dist:
            packages_for_dist = []
            package_lists[dist] = packages_for_dist
            r = requests.get(url)
            r.raise_for_status()

            gz = gzip.GzipFile(mode='r', fileobj=BytesIO(r.content))
            apt_package_string = gz.read().decode('utf-8').strip()
            packages_for_dist.extend(_parse_package_list(apt_package_string))

    return package_lists


def _parse_package_list(packages):
    for package in packages.split('\n\n'):
        if package.strip() != '':
            try:
                # The format is so similar to yaml that this works most of the time,
                # including for multiline descriptions, except if the description contains
                # colon (:) or other special characters that has meaning in yaml.
                yield yaml.load(package)
            except yaml.scanner.ScannerError as e:
                logger.error(
                    'Failed to parse package from PPA ({name})'.format(name=package.split('\n')[0]))
                logger.debug(package)
                logger.debug(e, exc_info=True)
                logger.info('Ignoring the error. Continuing parsing the rest of the packages.')
