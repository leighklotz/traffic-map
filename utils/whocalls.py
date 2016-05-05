#!/usr/bin/env python

from __future__ import print_function
import json
import csv
import sys

class WhoCalls(object):
    def __init__(self):
        self.ip_to_node_table = {}
        self.links = None
        self.nodes = None

    # ips.txt
    # TSV: REGION	NAME	INSTANCE_TYPE	ARCHDOMAIN	ENV_TAG	IP1	IP2...
    def read_ips(self, ips_txt):
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
                      if name != "unknown":
                          archdomain = archdomain + "/" + name
                      else:
                          archdomain = archdomain + "/" + ip
                      self.ip_to_node_table[ip] = {
                          'env': env_tag,
                          'archdomain': archdomain,
                          'instance_type': instance_type,
                          'region': region,
                          'name': name
                      }


    def read_instances(self, fn):
        with open(fn, 'r') as f: 
            j=json.load(f)


            self.links = j['links']
            self.nodes = j['nodes']

    def whocalls_ip(self, ip):
        a = set([link['target_name'] for link in self.links if link['source_name'] == ip])
        b = set([link['source_name'] for link in self.links if link['target_name'] == ip])

        who = a.union(b)

        return [node for node in self.nodes if node['name'] in who]

    def describe_ip(self, ip):
        return self.ip_to_node_table[ip]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: whocalls.py 2016-02-19 10.232.13.225")
        sys.exit(-1)
    date = sys.argv[1] # 2016-02-19
    ip = sys.argv[2] # 10.232.13.225
    fn = '/mnt/klotz/visualization/data/instances-%s.json' % date
    ips = '/mnt/klotz/data/netgraph-dat-%s/ips.txt' % date
    who_calls = WhoCalls()
    who_calls.read_ips(ips)
    who_calls.read_instances(fn)
    nodes = who_calls.whocalls_ip(ip)

    d = who_calls.describe_ip(ip)
    print("WHO CALLS OR IS CALLED BY", d['region'], d['env'], d['archdomain'], d['name'], ip)
    print("")
    for node in sorted(nodes, key=lambda x: (x['region'], x['env'], x['archdomain'], x['label'], x['name'])):
        print(node['region'], node['env'], node['archdomain'], node['label'], node['name'])

