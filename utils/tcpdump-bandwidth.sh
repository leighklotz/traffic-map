#!/bin/sh

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh

echo $DATDIR

./tcpdump-bandwidth.py ${DATDIR}/

