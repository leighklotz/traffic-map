#!/usr/bin/python

import boto.ec2

def sanitize(name):
    if name == None:
        return None
    else:
        return name.replace("<", "").replace(">","").replace(" ", "_")

def get_all_instances(ec2):
    try:
        return ec2.get_all_instances()
    except:
        return []


results = []
for region in boto.ec2.regions():
    ec2 = region.connect()
    reservations = get_all_instances(ec2)
    for reservation in reservations:
        for i in reservation.instances:
            results.append((i.id, i.instance_type))

for line in results:
    print("{}\t{}".format(*line))
