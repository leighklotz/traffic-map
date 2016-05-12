#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh
. ${TOP}/venv/bin/activate

DAT=${DATDIR}/all.dat
JSON=${OUTPUT}/instances-${YMD}.json

if [ ! -f ${DAT}.gz ]
then
  echo "$0: Uncompressing ${DAT}.gz"
  gunzip ${DAT}.gz
fi

echo "$0: Producing JSON=${JSON} from DAT=${DAT} and IPS=${IPS}"
export PYTHONPATH=${PYTHONPATH}:${DIR}/..
python ./convert-dat-to-json.py ${IPS} ${FOREIGN_IPS} ${DAT} ${JSON}
echo "$0: Produced JSON=${JSON} from DAT=${DAT} and IPS=${IPS}"

echo "$0: Compressing ${DAT}"
gzip ${DAT}
