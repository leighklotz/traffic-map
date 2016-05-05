#!/usr/bin/python

import csv
import sys

from instance_pricing import InstancePricing

def price_tsv_file(self, tsv_file):
    instance_pricing = InstancePricing()

    # us-east-1	ip-10-158-78-163.ec2.internal	m1.large	unknown	dev	174.129.137.152	10.158.78.163
    with open(tsv_file,'rb') if tsv_file != '-' else sys.stdin as tsvin:
        tsvin = csv.reader(tsvin, delimiter='\t')
        tsvout = csv.writer(sys.stdout, delimiter='\t')
        for row in tsvin:
            region = row[0]
            name = row[1]
            instance_type = row[2]
            archdomain = row[3]
            env_tag = row[4]
            ip_addresses = row[5:]
            price = instance_pricing.get_pricing(region, instance_type)
            tsvout.writerow([price, region, name, instance_type, archdomain, env_tag] + ip_addresses)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: {} ips.txt|-".format(sys.argv[0]))
        exit(-1)
    price_tsv_file(sys.argv[1])
