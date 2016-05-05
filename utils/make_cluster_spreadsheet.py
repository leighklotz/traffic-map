#!/usr/bin/env python

from __future__ import print_function

import json
import re
from collections import defaultdict


def get_clusters(filename):
    with open(filename, 'r') as f:
        clusters = json.load(f)
    return clusters


def diagonalize_links(nested_links):
    d = defaultdict(set)
    for from_name, to_names in nested_links.items():
        d[from_name].update(to_names.keys())
        for to_name in to_names.keys():
            d[to_name].add(from_name)
    return d


def main(fn,
         skip_env="^external|^aws-external",
         keep_archdomain="^online",
         skip_archdomain="^online/orchestration/fastapi"):
    c = get_clusters(fn)

    nested_links = diagonalize_links(c['nested_links'])
    skip_env_re = re.compile(skip_env)
    keep_archdomain_re = re.compile(keep_archdomain)
    skip_archdomain_re = re.compile(skip_archdomain)

    print('\t'.join(['env', 'from', 'to']))
    for from_name,to_names in sorted(nested_links.items()):
        from_env,from_archdomain = from_name.split("|")
        if not skip_env_re.search(from_env) and not skip_archdomain_re.search(from_archdomain) and keep_archdomain_re.search(from_archdomain):
            print("{}\t{}\t".format(from_env, from_archdomain), end='')

            for to_name in sorted(to_names):
                to_env,to_archdomain = to_name.split("|")
                if not skip_env_re.search(to_env) and not skip_archdomain_re.search(to_archdomain) and keep_archdomain_re.search(to_archdomain):
                    if from_env == to_env:
                        print(to_archdomain, end='\t')
                    else:
                        print(to_name, end='\t')
            print()


if __name__ == "__main__":
    main('/mnt/klotz/traffic-map/visualization/clusters-2016-04-22.json')
