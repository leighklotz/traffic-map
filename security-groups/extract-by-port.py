#!/usr/bin/env python

from __future__ import print_function

import json

def main():
    with open('security-groups-snapshot.json', 'r') as f:
        security_groups = json.load(f)['SecurityGroups']

    result = [ convert_group(group) for group in security_groups ]
    print(json.dumps(result))

def convert_group(group):
    return {
        'name': group['GroupName'],
        'id': group['GroupId'],
        "ingress": [
            ip_permission['FromPort'] for ip_permission in group['IpPermissions'] if ip_permission['IpProtocol'] == 'tcp'
        ]
    }

if __name__ == "__main__":
    main()

