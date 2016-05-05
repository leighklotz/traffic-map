#!/bin/bash

sleep_pid=`pidof sleep 86400`
if [ "$sleep_pid" == '' ]; then
  echo "not waiting"
  exit -1
fi

etime=`ps -p $sleep_pid -o etime=`
IFS=: read -r a b c <<<"${etime//[[:space:]]/}"
if [ "$c" == "" ] ; then
  h='0'; m=$((10#$a)); s=$((10#$b))
else
  h=$((10#$a)); m=$((10#$b)); s=$((10#$c))
fi
elapsed_seconds=$((($h * 60 + $m) * 60 + $s))
remaining_seconds=$((86400-$elapsed_seconds))
remaining_hours=$((remaining_seconds / 3600))
remaining_seconds=$(($remaining_seconds - 3600 * $remaining_hours))
remaining_minutes=$(($remaining_seconds / 60))
remaining_seconds=$(($remaining_seconds - 60 * $remaining_minutes))
printf "%02d:%02d:%02d\n" $remaining_hours $remaining_minutes $remaining_seconds
