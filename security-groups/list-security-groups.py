#!/usr/bin/env python

from __future__ import print_function

import boto.ec2
import boto.exception


def get_name(i):
    return i.tags.get('Name', i)

def main():
    for region in boto.ec2.regions():
        ec2 = region.connect()
        if ec2 is not None:
            try:
                reservations = ec2.get_all_instances()
            except boto.exception.EC2ResponseError:
                reservations = []
            for reservation in reservations:
                for i in reservation.instances:
                    print(region.name, get_name(i), ",".join([r.name for r in i.groups]))


main()
