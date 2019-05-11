#!/usr/bin/env bash
set -eu
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
cd ~/buildinfo
DATE=$(date +'%Y%m%d %H-%M-%S')
set +u
pyenv activate
set -u
./buildinfo.py https://ci-production.zenterio.lan &> "${DATE}".log
mv *.csv /mnt/MethodsandTools/Jenkins\ build\ data/
echo "done" >> "${DATE}".log
