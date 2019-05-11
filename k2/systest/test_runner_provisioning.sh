#!/usr/bin/env bash
set -exu
sudo apt-get update
sudo apt-get install gdebi-core --yes

# TODO Move into vagrant boxes. There is currently no provisioning for them so we need to decide on how that should be handled
if [ $(hostname) == "vagrant-u14" ]; then
    sudo apt-get install python3.4-venv --yes
else
    sudo apt-get install python3-venv --yes
fi

sudo apt-get install socat --yes