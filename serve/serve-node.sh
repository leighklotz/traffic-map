#!/bin/bash

# apt-get install nodejs
# npm install -g http-server

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh

cd ${STATIC}

if [ ! -L data ] ; 
then
  echo "Symlink data to ${OUTPUT}"
  ln -s "${OUTPUT}" data
fi

http-server -p 8000 --follow-symlinks --noCache=true
