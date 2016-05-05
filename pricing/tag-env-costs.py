#!/usr/bin/python

import sys
import csv
from collections import defaultdict
import operator


def read_ips(ips_txt):
  envs = dict()
  with open(ips_txt,'rb') as tsvin:
    tsvin = csv.reader(tsvin, delimiter='\t')
    for parsed in tsvin:
      i = 0
      if len(parsed) > 0:
        region = parsed[i].lower(); i += 1
        name = parsed[i].lower(); i += 1
        instance_type = parsed[i].lower(); i += 1
        price = float(parsed[i]); i+= 1
        archdomain = archdomain_fixup(parsed[i].lower()); i += 1
        env_tag = parsed[i].lower(); i += 1

        if env_tag not in envs:
          envs[env_tag] = defaultdict(float)
        tags = envs[env_tag]

        tags[archdomain] += price
  return envs


def main(ips_txt, prefix):
    envs = read_ips(ips_txt)
    env_costs = dict()
    env_rollups = dict()
    total_cost = 0

    for env_name, tags in envs.items():
      env_costs[env_name] = dict()
      costs = env_costs[env_name]
      env_rollups[env_name] = defaultdict(lambda: [0] * 4)
      rollups = env_rollups[env_name]

      for tag,price in tags.items():
          cost = price
          dots = 2
          costs[tag] = [round(cost, dots), round(cost * 24, dots), round(cost * 24*30, dots), round(cost * 24 * 365, dots)]
          tag_splits = tag.split("/")

          for i in range(0, len(tag_splits)):
              tag_prefix = '/'.join(tag_splits[0:i+1])
              rollups[tag_prefix] = map(operator.add, rollups[tag_prefix], [round(cost, dots), round(cost * 24, dots), round(cost * 24*30, dots), round(cost * 24 * 365, dots)])

      env_cost = sum(map(lambda x: x[0], costs.values()))
      total_cost += env_cost

    print("# Total cost for all envs")
    print(total_cost)

    for env_name, costs in env_costs.items():
      accumulated_cost = 0
      fn = "{}-{}-details.csv".format(prefix, env_name)
      print("# " + fn)
      with open(fn, 'w') as f:
        f.write("# Details for {}\n".format(env_name))
        f.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format("tag", "$hourly", "$daily", "$monthly", "$yearly", "$accumulated", "%-of-{}".format(total_cost), "accumulated-%-of-{}".format(total_cost)))
        for tag in sorted(costs, key=lambda k: costs[k][1], reverse=True):
            cost = costs[tag]
            accumulated_cost += cost[0]
            f.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(tag, cost[0], cost[1], cost[2], cost[3], accumulated_cost, round(cost[0]/total_cost, 2), round(accumulated_cost/total_cost, 2)))

    for env_name, rollups in env_rollups.items():
      fn = "{}-{}-rollup.csv".format(prefix, env_name)
      print("# " + fn)
      with open(fn, 'w') as f:
        f.write("# Rollup for {}\n".format(env_name))

        f.write("{}\t{}\t{}\t{}\t{}\t{}\n".format("tag", "$hourly", "$daily", "$monthly", "$yearly", "% of {}".format(total_cost)))
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
            f.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(short_tag, cost[0], cost[1], cost[2], cost[3], cost[0] / total_cost))


def archdomain_fixup(archdomain):
  if archdomain.startswith("offline/midtier/scoring"):
    return archdomain.replace("offline/midtier/scoring", "online/midtier/scoring")
  else:
    return archdomain


if __name__ == "__main__":
    # input file, output prefix
    main(sys.argv[1], sys.argv[2])
