#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh

echo ${IPS}

export PYTHONPATH=${PYTHONPATH}:${DIR}/..
#${DIR}/tag-costs.py ${IPS} | column -t
${DIR}/tag-costs.py ${IPS} 

