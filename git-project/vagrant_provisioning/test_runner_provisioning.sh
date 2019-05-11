set -exu
sudo apt-get update
sudo apt-get install gdebi-core python3-pip --yes

sudo update-locale LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8 LC_ALL=en_US.UTF-8
sudo pip3 install --upgrade pip

sudo pip3 install -r /vagrant/systest/requirements.txt

