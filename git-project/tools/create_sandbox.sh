#!/usr/bin/env bash

# Create a git project sandbox with bare git repositories.
#
# Argument list:
# $1 - path to directory
#
# Will create the directory and create three bare git repositories there.
# Will refuse to run if the directory exists.

topdir="$1"
if [ -e "${topdir}" ]
then
  echo "${topdir} exists, will not create a sandbox there." >&2
  exit 1
fi

mkdir -p "${topdir}"
cd "${topdir}"
REPO_BASE="$(pwd)"
git init -q --bare project.git
git init -q --bare product.git
git init -q --bare tools.git

git clone -q project.git 2>/dev/null
git clone -q product.git 2>/dev/null
git clone -q tools.git 2>/dev/null

for repo in project product tools
do
  pushd "$repo" &>/dev/null
  echo "$repo" > "$repo.txt"
  git add "$repo.txt"
  git commit -q -m "initial commit"
  git push -q origin master:master
  popd &>/dev/null
done

pushd project &>/dev/null
git submodule -q add -b master "${REPO_BASE}/product.git" src/product
git submodule -q add -b master "${REPO_BASE}/tools.git" tools
git commit -q --amend -C HEAD
git push -q -f origin master:master
popd &>/dev/null

rm -rf project product tools

echo "You sandbox is ready for (ab)use."
echo "To start working, run:"
echo "git project clone '$topdir/project.git'"
