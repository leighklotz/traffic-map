#!/usr/bin/python

import sys
import csv
from collections import Counter, defaultdict
from functools import partial
import operator
from pprint import pprint

import instance_pricing

def read_ips(ips_txt):
  tags = defaultdict(partial(defaultdict, Counter))
  with open(ips_txt,'rb') as tsvin:
    tsvin = csv.reader(tsvin, delimiter='\t')
    for parsed in tsvin:
      i = 0
      if len(parsed) > 0:
        region = parsed[i].lower(); i += 1
        name = parsed[i].lower(); i += 1
        instance_type = parsed[i].lower(); i += 1
        archdomain = parsed[i].lower(); i += 1
        if archdomain.startswith("offline/midtier/scoring"):
          archdomain = archdomain.replace("offline/midtier/scoring", 
                                          "online/midtier/scoring")
        env_tag = parsed[i].lower(); i += 1
        tags[archdomain][region][instance_type] += 1
  return tags

def main(ips_txt):
    instance_pricer = instance_pricing.InstancePricing()
    tags = read_ips(ips_txt)
    costs = dict()
    rollups = defaultdict(lambda : [0] * 4)
    for tag,regions in tags.items():
        cost = 0
        for region,instance_types in regions.items():
            for instance_type,count in instance_types.items():
                cost += (count * instance_pricer.get_pricing(region, instance_type))
            dots = 2
            costs[tag] = [round(cost, dots), round(cost * 24, dots), round(cost * 24*30, dots), round(cost * 24 * 365, dots)]
            tag_splits = tag.split("/")

            for i in range(0, len(tag_splits)):
                tag_prefix = '/'.join(tag_splits[0:i+1])
                rollups[tag_prefix] = map(operator.add, rollups[tag_prefix], [round(cost, dots), round(cost * 24, dots), round(cost * 24*30, dots), round(cost * 24 * 365, dots)])
    
    total_cost = sum(map(lambda x: x[0], costs.values()))
    accumulated_cost = 0

    print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format("tag", "hourly", "daily", "monthly", "yearly", "accumulated", "%"))
    for tag in sorted(costs, key=lambda k: costs[k][1], reverse=True):
        cost = costs[tag]
        accumulated_cost += cost[0]
        print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(tag, cost[0], cost[1], cost[2], cost[3], accumulated_cost, round(accumulated_cost/total_cost, 2)))


    print("# Rollups")

    print("{}\t{}\t{}\t{}\t{}".format("tag", "hourly", "daily", "monthly", "yearly"))
    previous_tag = None
    for tag in sorted(rollups, key=lambda k: k, reverse=False):
        cost = rollups[tag]
        common_initial_substring_length = 0
        if previous_tag is not None:
            common_initial_substring_length = map(operator.eq, previous_tag.split('/'), tag.split('/')).count(True)
        short_tag = tag
        if common_initial_substring_length:
            k = reduce(operator.add, map(len, previous_tag.split('/')[0:common_initial_substring_length]))
            left =  ('_' * k)
            right = ''.join(tag.split('/')[common_initial_substring_length:])
            short_tag = left + right
        previous_tag = tag
        print("{}\t{}\t{}\t{}\t{}".format(short_tag, cost[0], cost[1], cost[2], cost[3]))


if __name__ == "__main__":
    main(sys.argv[1])
