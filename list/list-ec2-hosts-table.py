#!/usr/bin/python

from __future__ import print_function

import argparse
import boto.ec2
import dateutil
import datetime
import json

from pricing.instance_pricing import InstancePricing
from pricing.spot_pricing import SpotPricing

# region.name, name, instance_type, price, archdomain, env_tag, ip_address, private_ip_address ...

def sanitize(value):
    if value is None or value == "":
        return "unknown"
    else:
        return value.replace("<", "").replace(">","").replace(" ", "_")

def get_host_name(i):
    # Sometimes instances transiently don't have names
    if 'Name' in i.tags:
        return sanitize(i.tags['Name'])
    else:
        return "unknown"

def get_archdomain(i):
    if 'archdomain' in i.tags:
        return sanitize(i.tags['archdomain'])
    else:
        return "unknown"

def get_env_tag(i):
    if 'env' in i.tags:
        return sanitize(i.tags['env'])
    else:
        return "unknown"

def get_all_instances(ec2):
    try:
        return ec2.get_all_instances()
    except:
        return []

def main(args):
    instance_pricer = InstancePricing()
    spot_pricer = SpotPricing()
    results = []
    for region in boto.ec2.regions():
        ec2 = region.connect()
        reservations = get_all_instances(ec2)

        for reservation in reservations:

            for i in reservation.instances:
                name = get_host_name(i)
                archdomain = get_archdomain(i)
                env_tag = get_env_tag(i)

                if i.ip_address and i.private_ip_address and name:
                    if i.spot_instance_request_id is not None:
                        start_time = dateutil.parser.parse(i.launch_time)
                        end_time = datetime.datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
                        hourly_price = spot_pricer.get_spot_instance_pricing(i.instance_type, start_time, end_time,
                                                                             i.placement, i.spot_instance_request_id)
                    else:
                        hourly_price = instance_pricer.get_ondemand_pricing(region.name, i.instance_type)

                    results.append((region.name, name, i.instance_type, str(hourly_price), archdomain, env_tag, i.ip_address, i.private_ip_address))

    if args.format=='tsv':
        for line in results:
            print("\t".join(line))
    elif args.format=='json-lines':
        for line in results:
            print(json.dumps(dict(zip(['region', 'name', 'type', 'price', 'archdomain', 'env', 'ip_public', 'ip_private'], line))))
    elif args.format=='json':
        print('[')
        for line in results:
            print(json.dumps(dict(zip(['region', 'name', 'type', 'price', 'archdomain', 'env', 'ip_public', 'ip_private'], line))), end=',\n')
        print(']')
    else:
        raise ValueError("--format tsv|json|json-lines")


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=main)
    parser.add_argument('--format', default='tsv')
    args = parser.parse_args()
    args.func(args)
