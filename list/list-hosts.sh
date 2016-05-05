#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
. ../config/config.sh

echo "$0: List Hosts to ${HOSTS_TXT}"

HOSTS=""
 while read region name instance_type archdomain price env_tag external_ip internal_ip
 do           
   if [ $region == "$REGION" ]; then
       HOSTS="$HOSTS ${internal_ip}"
   else
     echo "$0 Skipping host: $name (in $region, not $REGION)"
   fi
 done < $IPS

echo "$0: Collection of hosts determined in ${HOSTS_TXT}"
echo $HOSTS > ${HOSTS_TXT}
