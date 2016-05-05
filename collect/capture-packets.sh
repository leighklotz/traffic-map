#!/bin/bash
# Capture to a temp name, then rename
fn_temp=/tmp/captured-packets-$$.tmp
fn_out=/tmp/captured-packets.dat
( cmdpid=$BASHPID; (sleep 60; kill $cmdpid) & exec tcpdump -n -c 1000 -U > ${fn_temp} 2> /dev/null )
mv ${fn_temp} ${fn_out}
