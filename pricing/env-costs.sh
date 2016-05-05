#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh

echo $IPS

echo "Daily and monthly costs, with some overlap between env"

export PYTHONPATH=${PYTHONPATH}:${DIR}/..

printf "%s	daily	monthly	yearly\n" "env"
for env_tag in `cat $IPS | awk '{print $5; }' | sort | uniq`
do 
  printf "%s	" $env_tag; cat $IPS | grep "	$env_tag	"|python ${DIR}/instance_pricing.py -|awk '{sum += $1; } END { printf "%.0f\t%.0f\t%.0f\n", sum * 24, sum * 24 * 30, sum * 24 * 365; }'
done

printf "%s	" "total	"; cat $IPS | python ${DIR}/instance_pricing.py -|awk '{sum += $1; } END { printf "%.0f\t%.0f\t%.0f\n", sum * 24, sum * 24 * 30, sum * 24 * 365; }'
