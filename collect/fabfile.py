#!/usr/bin/python

import sys
from ConfigParser import SafeConfigParser

from fabric.api import run, parallel, env, put, get, sudo
from fabric.exceptions import NetworkError

config = SafeConfigParser()
config.read('fabconfig.ini')
for k,v in config.items('env'):
    env[k] = v
remote_script_directory = config.get('var', 'remote_script_directory')

# read password silently on stdin
#  --initial-password-prompt does not read from stdin so a script cannot pass
# the password safely
env.password = sys.stdin.readline().rstrip()


env.use_ssh_config = True
env.warn_only = True
env.skip_bad_hosts = True

local_capture_packets_script = "capture-packets.sh"
remote_capture_packets_script = "{}/capture-packets.sh".format(remote_script_directory)

@parallel
def capture_packets():
    try:
        put(local_capture_packets_script, remote_capture_packets_script, mode=0755)
        sudo(remote_capture_packets_script)
        get('/tmp/captured-packets.dat', '{}/host-{}.dat'.format(env.DATDIR, env.host))
    except NetworkError as ex:
        print(str(ex))

@parallel
def get_lsb_release():
    try:
        get('/etc/lsb-release', '{}/lsb-release-{}.dat'.format(env.DATDIR, env.host))
    except NetworkError as ex:
        print(str(ex))

@parallel
def get_uptime_load():
    try:
        get('/proc/uptime', '{}/uptime-{}.dat'.format(env.DATDIR, env.host))
        get('/proc/loadavg', '{}/loadavg-{}.dat'.format(env.DATDIR, env.host))
        get('/proc/meminfo', '{}/meminfo-{}.dat'.format(env.DATDIR, env.host))
    except NetworkError as ex:
        print(str(ex))

