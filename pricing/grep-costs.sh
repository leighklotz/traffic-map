#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh

echo $IPS

echo "Daily and monthly costs for $1"
echo ""
export PYTHONPATH=${PYTHONPATH}:${DIR}/..
cat $IPS | grep "$1" | python ${DIR}/instance_pricing.py -

echo ""
echo ""

printf "%-16s	daily	monthly	yearly\n" "match"
printf "%-16s: " $1; cat $IPS | grep "$1"|python ${DIR}/instance_pricing.py -|awk '{sum += $1; } END { printf "$%.0f\t$%.0f\t$%.0f\n", sum * 24, sum * 24 * 30, sum * 24 * 365; }'

