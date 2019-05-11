HYDRA
=====

Hydra is a small web application that can clone a repository and checkout a given
branch/hash/tag using a fairly simple URL scheme.

Hydra runs on Apache2, PHP, using the open source library Code Igniter (https://codeigniter.com/).

Hydra does an actual checkout for each SHA to allow for features that requires
an actual file-system.

PREREQUISITES
-------------

* Apache2 Webserver
* php5+
* git
* unzip (used during the installation)
* bc (used during the installation)

The prerequisites will be installed if not present.

INSTALLATION
------------

    sudo make install

Configure /etc/hydra/hydra.php:
* Set which repositories that can be accessed
* Set base_url for the system or leave as is if accessed using multiple hosts
* Set path to remote git repository server

Remote git repository access:
* Place a id_rsa private key at /etc/hydra/id_rsa with:
    - ownership root:www-data
    - permissions 440.
* Add the remote servers identification key to /etc/hydra/known_hosts:

    `ssh-keyscan -H -t ecdsa SERVER 2> /dev/null | sudo tee -a /etc/hydra/known_hosts`

When doing reinstall, the existing configuration will be overwritten - unless:

    sudo HYDRA_KEEP_CONFIG=true make install


LOGGING
-------

The loglevel can be adjusted by changing the x value in config/config.php

    $config['log_threshold'] = x;
    0 => no logging
    .
    .
    .
    4 => everything

Logfiles of interest could be:
* /var/log/apache2/error.log
* /var/log/hydra/log-yyyy-mm-dd.php

DEVELOPMENT
-----------
Run test in vagrant on Ubuntu-12, Ubuntu-14, Ubuntu-16:

    make check

Tests can be run on single system (e.g.):

    make vagrant_systest_u12

If PHP is installed on the local system, lint can be run using:

    make lint

System tests require intrusive installations of authorized_keys and known hosts
and it is therefore prevented from being installed on a regular system by checking
for the SUDO_USER vagrant.
