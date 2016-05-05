#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh

echo ${IPS}

OUTPUT_PREFIX=`dirname ${IPS}`/costs

export PYTHONPATH=${PYTHONPATH}:${DIR}/..
#${DIR}/tag-env-costs.py ${IPS} | column -t
${DIR}/tag-env-costs.py ${IPS} ${OUTPUT_PREFIX}

