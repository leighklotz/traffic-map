#!/usr/bin/env python

import sys
import json

def read_json(fn):
    print(fn)
    with open(fn, 'r') as f:
        return json.load(f)

def parse_env(e):
    return e.split("|")[0]

def main(cluster_fn):
    nested_links = read_json(cluster_fn)['nested_links']
    crosses = set()
    for src,dest_dict in nested_links.items():
        src_env = parse_env(src)
        for dest,values in dest_dict.items():
            dest_env =parse_env(dest)
            if src_env != dest_env:
                crosses.add("{} -> {} on ports {}".format(src, dest, ','.join([ str(x) for x in values['ports']])))
                crosses.add("{} -> {} on ports {}".format(dest, src, ','.join([ str(x) for x in values['ports']])))
    for line in sorted(crosses):
        print(line)

if __name__ == "__main__":
    main(sys.argv[1])
