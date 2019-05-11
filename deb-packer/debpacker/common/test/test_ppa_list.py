import gzip
from io import BytesIO
from unittest import TestCase

import requests_mock

from debpacker.common.ppa_list import _parse_package_list, retrieve_package_lists, \
    retrieve_package_version_mapping


class TestPpaList(TestCase):

    def test_parse_packages_list(self):
        parsed_list = list(_parse_package_list(packages_txt))
        self.assertEqual(len(parsed_list), 3)
        self.assertEqual(parsed_list[2]['Package'], 'zenterio-crosstools')
        self.assertEqual(parsed_list[2]['Version'], '1.0.2')

    def test_retrieve_package_lists_for_single_dist(self):
        gz_content = BytesIO()
        gzip.GzipFile(mode='w', fileobj=gz_content).write(packages_txt.encode('utf-8'))
        with requests_mock.mock() as r:
            r.get('http://url', content=gz_content.getvalue())
            packages = retrieve_package_lists({'trusty': 'http://url'})
            self.assertEqual(len(packages['trusty']), 3)

    def test_retrieve_package_lists_for_multiple_dists(self):
        gz_content = BytesIO()
        gzip.GzipFile(mode='w', fileobj=gz_content).write(packages_txt.encode('utf-8'))
        with requests_mock.mock() as r:
            r.get('http://url', content=gz_content.getvalue())
            r.get('http://url2', content=b'')
            packages = retrieve_package_lists({'trusty': 'http://url', 'xenial': 'http://url2'})
            self.assertEqual(len(packages['trusty']), 3)
            self.assertEqual(len(packages['xenial']), 0)

    def test_retrieve_package_lists_with_dist_filter(self):
        gz_content = BytesIO()
        gzip.GzipFile(mode='w', fileobj=gz_content).write(packages_txt.encode('utf-8'))
        with requests_mock.mock() as r:
            r.get('http://url2', content=b'')
            packages = retrieve_package_lists(
                {
                    'trusty': 'http://url',
                    'xenial': 'http://url2'
                }, filter_dist='xenial')
            self.assertEqual(len(packages['xenial']), 0)
            self.assertNotIn('trusty', packages)

    def test_retrieve_package_lists_raises_on_http_error_status(self):
        with requests_mock.mock() as r:
            r.get('http://url', status_code=404)
            self.assertRaises(Exception, retrieve_package_lists, {'trusty': 'http://url'})

    def test_retrieve_version_mapping(self):
        gz_content = BytesIO()
        gzip.GzipFile(mode='w', fileobj=gz_content).write(packages_txt.encode('utf-8'))
        with requests_mock.mock() as r:
            r.get('http://url', content=gz_content.getvalue())
            self.assertEqual(
                retrieve_package_version_mapping({
                    'trusty': 'http://url'
                }), {
                    'trusty': {
                        'dh-virtualenv': '0.11-1',
                        'vagrant': '1:1.8.5',
                        'zenterio-crosstools': '1.0.2'
                    }
                })

    def test_retrieve_version_mapping_for_multiple_dist(self):
        gz_content = BytesIO()
        gzip.GzipFile(mode='w', fileobj=gz_content).write(packages_txt.encode('utf-8'))
        with requests_mock.mock() as r:
            r.get('http://url', content=gz_content.getvalue())
            r.get('http://url2', content=b'')
            self.assertEqual(
                retrieve_package_version_mapping({
                    'trusty': 'http://url',
                    'xenial': 'http://url2'
                }), {
                    'trusty': {
                        'dh-virtualenv': '0.11-1',
                        'vagrant': '1:1.8.5',
                        'zenterio-crosstools': '1.0.2'
                    },
                    'xenial': {}
                })


packages_txt = """\
Package: dh-virtualenv
Version: 0.11-1
Architecture: all
Maintainer: Jyrki Pulliainen <jyrki@spotify.com>
Installed-Size: 256
Depends: python (>= 2.7), python (<< 2.8), virtualenv | python-virtualenv (>= 1.7)
Homepage: http://www.github.com/spotify/dh-virtualenv
Priority: extra
Section: python
Filename: pool/main/d/dh-virtualenv/dh-virtualenv_0.11-1_all.deb
Size: 38598
SHA256: f7ced20fdf9d8bd0515ef6b7c6159b4c556f0c93a6b79e57e708ca20faab5caf
SHA1: b37a7996c75f7fe0e1f8733dfbc99c4dce1048fc
MD5sum: f89144719e899f58867ccb4fe2993486
Description: wrap and build python packages using virtualenv
 This package provides a dh sequencer that helps you to deploy your
 virtualenv wrapped installation inside a Debian package.

Package: vagrant
Version: 1:1.8.5
License: unknown
Vendor: root@vagrant-package-ubuntu-32
Architecture: i386
Maintainer: HashiCorp <support@hashicorp.com>
Installed-Size: 176025
Homepage: https://www.vagrantup.com/
Priority: extra
Section: default
Filename: pool/main/v/vagrant/vagrant_1.8.5_i386.deb
Size: 73707674
SHA256: 978b3bf384d7a4b636554eaf988976f3797e7e41801cf8e356ff7e0574c9fa9a
SHA1: afaad7dd5cea96ba72a65eecc9f9c17fd8205199
MD5sum: 9b65c81498e3ad75e64c7ef86a5e2600
Description: no description given

Package: zenterio-crosstools
Version: 1.0.2
Architecture: all
Maintainer: Engineering Services <engineering-services@zenterio.com>
Installed-Size: 176192
Pre-Depends: dpkg (>= 1.16.1)
Priority: extra
Section: devel
Filename: pool/main/z/zenterio-crosstools_1.0.2_all.deb
Size: 30933198
SHA256: a7b692ddb0646660c2931627b84f65e7e7e6259576b564e3e5a2fa8abcc4f8b1
SHA1: b8e8b2f2e6023391e218a40a204042d3de4683ea
MD5sum: 3e142ea3670ca7ec9d8f9e3ef5b09cac
Description: Toolchain crosstools_hf-linux-2.6.18.0_gcc-4.2-11ts_uclibc-nptl-0.9.29-20070423_20090508
 This toolchain is installed"""
