#!/usr/bin/env python

from __future__ import print_function
import sys
import operator
import re
from datetime import datetime
import glob
import itertools
import gzip
import csv


instance_bandwidth_mbit_table = {
    'm4.large': 450,            # moderate
    'm4.xlarge': 750,           # high
    'm4.2xlarge': 1000,         # high
    'm4.4xlarge': 2000,         # high
    'm4.10xlarge': 4000,        # 10 gb
    'c4.large': 500,
    'c4.xlarge': 750,
    'c4.2xlarge': 1000,
    'c4.4xlarge': 2000,
    'c4.8xlarge': 4000,
    # estimates
    't1.micro': 100,
    'c1.medium': 1000,
    'c1.xlarge': 1000,
    'c3.large': 500,
    'c3.xlarge': 900,
    'c3.2xlarge': 1100,
    'c3.4xlarge': 2200,
    'c3.8xlarge': 7500,
    'i2.8xlarge': 7500,
    'i2.4xlarge': 4000,
    'i2.2xlarge': 2000,
    'i2.xlarge': 1000,
    'm1.large': 800,
    'm1.medium': 800,
    'm1.small': 250,
    'm1.xlarge': 1000,
    'm2.2xlarge': 1000,
    'm2.4xlarge': 1000,
    'm2.xlarge': 300,
    'm3.2xlarge': 500,
    'm3.large': 700,
    'm3.medium': 400,
    'm3.xlarge': 1000,
    'r3.large': 300e6
}


def get_instance_bandwidth_mbit(instance_type):
    return instance_bandwidth_mbit_table[instance_type]


def str2datetime(s):
    parts = s.split('.')
    dt = datetime.strptime(parts[0], "%H:%M:%S")
    return dt.replace(microsecond=int(parts[1]))


def opener(fn):
    if fn.endswith('.gz'):
        return gzip.open(fn, "r")
    else:
        return open(fn, "r")


def ip_from_fn(fn):
    return re.search("([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})", fn).group(1)


# we could catch more traffic by inspecting the to/from lines, but we need to elimiate duplicate traffic if we do that,
# and that's painful.

def host_bandwidth(fn, host_table):
    first_line = None
    last_line = None
    bandwidth_sum = 0
    overhead_bytes_per_packet = 41

    ip = ip_from_fn(fn)
    for line in opener(fn):
        line = line.strip()
        if not first_line and line:
            first_line = line
        if line:
            bandwidth = re.match(r'^.*length ([0-9]+).*', line)
            if bandwidth:
                bandwidth_sum += int(bandwidth.group(1))
            bandwidth_sum += overhead_bytes_per_packet
            last_line = line

    first_date = re.match(r'([0-9:]+\.[0-9]+) ', first_line).group(1)
    last_date = re.match(r'([0-9:]+\.[0-9]+) ', last_line).group(1)

    elapsed_seconds = (str2datetime(last_date) - str2datetime(first_date)).total_seconds()

    bps = int(round(bandwidth_sum / elapsed_seconds))

    return { 'ip': ip,
             'bandwidth_sum': bandwidth_sum, 
             'elapsed_seconds': elapsed_seconds, 
             'bps': bps, 
             'instance_type': host_table[ip]['instance_type'] }


def calculate_host_stats(fn, host_table):
    hbw_stats = host_bandwidth(fn, host_table)
    hbw_stats['bandwidth_used_fraction'] = bandwidth_used_fraction(hbw_stats['bandwidth_sum'], hbw_stats['instance_type'])
    return hbw_stats

def all_hosts_bandwidth(netgraph_dir, host_table):
    usage = [
        calculate_host_stats(fn, host_table)
        for fn in itertools.chain(glob.iglob(netgraph_dir + "/host-*.dat"),
                                  glob.iglob(netgraph_dir + "/host-*.dat.gz"))
        
    ]
    return sorted(usage, key=operator.itemgetter('bandwidth_used_fraction'), reverse=True)


# ips.txt
# TSV: REGION	NAME	INSTANCE_TYPE	ARCHDOMAIN	ENV_TAG	IP1	IP2...
def read_ips(ips_txt):
    host_table = dict()
    with open(ips_txt,'rb') as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')
        for parsed in tsvin:
            i = 0
            if len(parsed) > 0:
                region = parsed[i].lower(); i += 1
                name = parsed[i].lower(); i += 1
                instance_type = parsed[i].lower(); i += 1
                archdomain = parsed[i].lower(); i += 1
                env_tag = parsed[i].lower(); i += 1
                for ip in parsed[i:]:
                    host_table[ip] = { 'name':name, 'env':env_tag, 'archdomain':archdomain, 'instance_type':instance_type, 'region':region }
    return host_table


def bandwidth_used_fraction(bandwidth_used, instance_type):
    expected_bandwidth = instance_bandwidth_mbit_table[instance_type]
    bits = bandwidth_used * 8
    megabits = bits / 1024.0 / 1024.0
    result = megabits / float(expected_bandwidth)
    return result


def main(netgraph_dir):
    host_table = read_ips(netgraph_dir + 'ips.txt')
    for result in all_hosts_bandwidth(netgraph_dir, host_table):
        ip = result['ip']
        bits = result['bandwidth_sum'] * 8
        megabits = bits / 1024.0 / 1024.0
        used_fraction = result['bandwidth_used_fraction']
        host = host_table[ip]
        name = host['name']
        archdomain = host['archdomain']
        env_tag = host['env']
        region = host['region']
        instance_type = host['instance_type']

        print('\t'.join([region, name, instance_type, archdomain, env_tag, ip, str(round(megabits, 1))+"Mb", str(round(used_fraction*100, 1))+'%']))


if __name__ == "__main__":
    # '/mnt/klotz/netgraph-dat-2015-11-11/'
    main(sys.argv[1])           # dirname

