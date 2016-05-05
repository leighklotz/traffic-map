#!/usr/bin/env python

from __future__ import print_function

from collections import defaultdict

import boto.ec2
import boto.exception

from security_group_archdomains import SECURITY_GROUP_ARCHDOMAINS
from heuristics import split_group_name

def get_name(i):
    return i.tags.get('Name', i)

def get_archdomain(i):
    return i.tags.get('archdomain', 'unknown')

def main():
    result = calculate_sg_archdomains()
    for sg_name,archdomains in result.items():
        label,env = split_group_name(sg_name)
        if len(archdomains) == 1:
            found_archdomain = list(archdomains)[0]
            expected_archdomain = SECURITY_GROUP_ARCHDOMAINS.get(label, None)
            if expected_archdomain != found_archdomain:
                print(label, expected_archdomain, found_archdomain)
        else:
            print("#", label, ",".join(archdomains))

def calculate_sg_archdomains():
    result = defaultdict(set)

    for region in boto.ec2.regions():
        ec2 = region.connect()
        if ec2 is not None:
            try:
                reservations = ec2.get_all_instances()
            except boto.exception.EC2ResponseError:
                reservations = []
            for reservation in reservations:
                for i in reservation.instances:
                    archdomain = get_archdomain(i)
                    for r in i.groups:
                        result[r.name].add(archdomain)

    return result


main()
