#!/usr/bin/python

import boto.ec2

def sanitize(name):
    if name == None:
        return None
    else:
        return name.replace("<", "").replace(">","").replace(" ", "_")

def get_host_name(i):
    # Sometimes instances transiently don't have names
    if 'Name' in i.tags:
        return sanitize(i.tags['Name'])
    else:
        return None

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
            name = get_host_name(i)
            if i.ip_address != None and i.private_ip_address != None and name != None:
                results.append((name, i.ip_address, i.private_ip_address, i.instance_type))

for line in results:
    print("{0}\t{1}\t{2}\t{3}".format(line[0], line[1], line[2], line[3]))
