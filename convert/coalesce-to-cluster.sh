#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh
. ${TOP}/venv/bin/activate


JSON=${OUTPUT}/instances-${YMD}.json
CLUSTER=${OUTPUT}/clusters-${YMD}.json

echo "$0: Producing CLUSTER=${CLUSTER} from JSON=${JSON}"
export PYTHONPATH=${PYTHONPATH}:${DIR}/..
python ./coalesce-to-cluster.py ${JSON} ${CLUSTER}
echo "$0: Produced CLUSTER=${CLUSTER} from JSON=${JSON}"
