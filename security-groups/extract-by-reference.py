#!/usr/bin/env python

from __future__ import print_function

import sys
import json
import gzip

from security_group_archdomains import SECURITY_GROUP_ARCHDOMAINS
from heuristics import split_group_name

OUR_USER_ID = "475669215534"

def main(argv):
    fn = argv[1]
    security_groups = None
    if (fn.endswith(".gz")):
        with gzip.GzipFile(fn, 'r') as f:
            security_groups = json.load(f)['SecurityGroups']
    else:
        with open(fn, 'r') as f:
            security_groups = json.load(f)['SecurityGroups']

    internal_nodes = [ convert_internal_group_to_node(group) for group in security_groups ]
    aws_external_nodes = map(dict, (set([ tuple(x.items()) for group in security_groups for x in convert_aws_external_group_to_nodes(group) ])))
    nodes = internal_nodes + aws_external_nodes
    decorate_with_index(nodes)

    node_index_table = { node['name']: i for i,node in enumerate(nodes)} 
    links = [ x for group in security_groups for x in convert_group_to_links(node_index_table, group) ]
    result = { 'nodes': nodes, 'links': links }
    print(json.dumps(result, indent=4, sort_keys=True))

def decorate_with_index(s):
    for i,v in enumerate(s):
        v['i'] = i


def calculate_archdomain(group_name, default_value='unknown'):
    label,env = split_group_name(group_name)
    return SECURITY_GROUP_ARCHDOMAINS.get(label, None) or default_value

def calculate_env(group_name):
    label,env = split_group_name(group_name)
    return env

def convert_internal_group_to_node(group):
    return {
        'name': group['GroupId'],
        'label': group['GroupName'],
        'description': group['Description'],

        'archdomain': calculate_archdomain(group['GroupName']),
        'traffic': 1,
        'env': calculate_env(group['GroupName']),
        'instance_type': 'unknown',
        'ip_type': 'internal',
        'price': 3.0,
        'region': 'us-west-1'   # crock
    }

def convert_aws_external_group_to_nodes(group):
    for source in group['IpPermissions']:
        for target in source['UserIdGroupPairs']:
            if target['UserId'] != OUR_USER_ID:
                yield {
                    'name': target['GroupId'],
                    'label': target['GroupName'],
                    'description': target['UserId'],

                    'archdomain': calculate_archdomain(target['GroupName'], default_value='aws-external'),
                    'traffic': 1,
                    'env': 'aws-external',
                    'instance_type': 'unknown',
                    'ip_type': 'external',
                    'price': 5.0,         # irrelevant but controls circle size in chart
                    'region': 'us-west-1'   # crock
                }


def convert_group_to_links(node_index_table, source_group):
    source_group_name = source_group['GroupName']
    source_group_id = source_group['GroupId']
    for source in source_group['IpPermissions']:
        if source['IpProtocol'] == 'tcp':
            for target in source['UserIdGroupPairs']:
                yield {
                    'source_name': source_group_id,
                    'source_label': source_group_name,
                    'source': node_index_table[source_group_id],
                    'target_name': target['GroupId'],
                    'target_label': target.get('GroupName', ''),
                    'target': node_index_table[target['GroupId']],
                    'value': 5,
                    'ports': [ source['FromPort'], source['ToPort'] ]
                }

if __name__ == "__main__":
    main(sys.argv)
