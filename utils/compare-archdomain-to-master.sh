#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh

echo "$0: Comparing ${MASTER_ARCHDOMAIN_TAGS} to instances"

export PYTHONPATH=${PYTHONPATH}:${DIR}/..
python ./compare-archdomain-to-master.py "${MASTER_ARCHDOMAIN_TAGS}"
