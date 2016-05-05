#!/bin/bash -u

# run this program under screen so you can detach it after typing the 
# password.  we don't have a good way to do the password otherwise.

# specify one arg, RUN_AT_TIME, to run in a loop.
# run with no args to run once immediately and exit.

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

. config/config.sh

function notify() {
   msg=${1}
   msg="$0 $$: ${msg}"
   echo "${msg}" | mail -s "${msg}" ${ADMIN_EMAIL}
}

function finish() {
  if [ "${RUN_AT_TIME}" != "" ] ;
  then
    notify "exiting...please restart"
  fi
}

function wait_until_then() {
  startTime=$(date +%s)
  endTime=$(date -d "${RUN_AT_TIME}" +%s)
  first_time_wait=$((${endTime} - ${startTime}))
  notify "Sleeping $first_time_wait until ${RUN_AT_TIME} before run"
  sleep ${first_time_wait}
  notify "Done sleeping $first_time_wait before run."
}

trap finish EXIT

notify "Password required"

echo -n "sudo password: "
read -s sudo_password
echo ""

# Specify RUN_AT_TIME if you don't want to run immediately.
# It will try to run at that time daily.  
# Otherwise it will run right away and again every 86400 seconds

RUN_AT_TIME=${1-''}

if [ "${RUN_AT_TIME}" != "" ] ;
then
  wait_until_then
fi

while true; 
do

    . config/config.sh

    notify "Creating OUTPUT=${OUTPUT} directory"
    mkdir -p ${OUTPUT}

    notify "Creating DATDIR=${DATDIR} directory"
    mkdir -p ${DATDIR}

    notify "Listing IPs"
    ${SCRIPTDIR}/list/list-ips.sh

    notify "Listing Hosts"
    ${SCRIPTDIR}/list/list-hosts.sh

    notify "Gathering traffic data from hosts"
    echo $sudo_password | ${SCRIPTDIR}/collect/gather-dat.sh <<< "$sudo_password"

    notify "Converting the traffic data to JSON"
    ${SCRIPTDIR}/convert/convert-dat-to-json.sh

    notify "Clustering the traffic data to JSON"
    ${SCRIPTDIR}/convert/coalesce-to-cluster.sh

    notify "Listing security groups"
    ${SCRIPTDIR}/security-groups/list-security-groups.sh

    notify "Archdomain Tag Report"
    ${SCRIPTDIR}/utils/compare-archdomain-to-master.sh | mail -s "Archdomain Tag Report" ${REPORT_EMAIL}

    notify "Backing up in background"
    ${SCRIPTDIR}/collect/backup.sh &

    if [ "${RUN_AT_TIME}" != "" ] ;
    then
        notify "Sleeping until tomorrow at ${RUN_AT_TIME}"
        wait_until_then
    else
        notify "Done and exiting"
        break
    fi

done
