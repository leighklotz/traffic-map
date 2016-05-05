#!/usr/bin/python

from __future__ import print_function

import operator
import json
import csv
import sys
import argparse


def pick(items, d):
   return { i:d[i] for i in items }


def calculate_cost(j, env_name, archdomain_prefix):
    env = j['envs'][env_name]
    env_online = [ env[x] for x in env if x.startswith(archdomain_prefix) ]
    env_online_short = map(lambda x: pick(["label", "price", "ips"], x), env_online)
    for i in env_online_short:
        i['size'] = len(i['ips'])
        i['yearly_cost'] = int(round(i['price'] * 24 * 365))
    return map(lambda x: pick(["label", "yearly_cost", "size"], x), env_online_short)


def csv_costs(j, env_name, archdomain_prefix):
    costs = calculate_cost(j, env_name, archdomain_prefix)
    total = reduce(operator.add, map(lambda x: x['yearly_cost'], costs))
    print("total", total)
    w = csv.DictWriter(sys.stdout, fieldnames=sorted(costs[0].keys()))
    w.writeheader()
    w.writerows(costs)
    return { 'env': env_name, 'archdomain_prefix': archdomain_prefix, 'yearly': reduce(operator.add, map(lambda x: x['yearly_cost'], costs))}


def show_yearly_costs(r):
    print("yearly cost env={} archdomain_prefix={} is {}".format(r['env'], r['archdomain_prefix'], r['yearly']))

def show_yearly_cost_comparison(current, previous):
    assert current['env'] == previous['env']
    assert current['archdomain_prefix']  == previous['archdomain_prefix']
    print("yearly cost improvement env={} archdomain_prefix={} is {}".format(current['env'], current['archdomain_prefix'], previous['yearly'] - current['yearly']))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--clusters")
    parser.add_argument("--previous_clusters", help="If specified, compare current total to this previous total")
    parser.add_argument("--env")
    parser.add_argument("--archdomain_prefix", nargs="?", default="")

    args = parser.parse_args()

    print(args, args.archdomain_prefix)

    if args.clusters:
        with open(args.clusters, 'r') as f:
            current = csv_costs(json.load(f), env_name=args.env, archdomain_prefix=args.archdomain_prefix)
            show_yearly_costs(current)

    if args.previous_clusters:
        with open(args.previous_clusters, 'r') as f:
            previous = csv_costs(json.load(f), env_name=args.env, archdomain_prefix=args.archdomain_prefix)
            show_yearly_costs(previous)

    if args.clusters and args.previous_clusters:
        show_yearly_cost_comparison(current, previous)
            
