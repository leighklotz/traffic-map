#!/usr/bin/env python

from __future__ import print_function

import sys
import csv
import re
import boto.ec2

def safe_connect(r):
    try:
        return r.connect()
    except:
        return None


def safe_get_all_instances(ec2):
    try:
        return ec2.get_all_instances()
    except :
        return []


def running_instances():
    for r in boto.ec2.regions():
        ec2 = safe_connect(r)
        if ec2:
            for reservation in safe_get_all_instances(ec2):
                for i in reservation.instances:
                    if i.state == 'running':
                        yield i


def get_observed_tags():
    return set([ i.tags.get('archdomain', '<untagged>') for i in running_instances() ])

def main(master_fn):
    master_list = read_master_csv(master_fn)
    observed_list = get_observed_tags()
    show_observed_tags_not_in_master(master_list, observed_list)
    show_master_tags_not_in_observed(master_list, observed_list)

def show_observed_tags_not_in_master(master_list, observed_list):
    print("# Unrecognized archdomain tags")
    for tag in observed_list:
        tag_match = find(lambda t: matches_tag(t, tag), master_list)
        if tag_match is None:
            subtag_match = find(lambda t: matches_subtag(t, tag), master_list)
            if subtag_match is None:
                print(tag)

def show_master_tags_not_in_observed(master_list, observed_list):
    print("# No instances with these tags:")
    for tag in master_list:
        tag_match = find(lambda t: matches_tag(tag, t), observed_list)
        if tag_match is None:
            subtag_match = find(lambda t: matches_subtag(tag, t), observed_list)
            if subtag_match is None:
                print(tag)

def read_master_csv(fn):
    with open(fn, 'rb') as f:
        tags = [ x[0] for x in csv.reader(f, delimiter=',') ]
        header = tags[0]
        return tags[1:]


def matches_tag(tag_template, tag):
    tag_re = "^" + re.sub("{[^}]+}", "[^/]+", tag_template) + "$"
    result = re.compile(tag_re).search(tag)
    return result is not None


def matches_subtag(tag_template, tag):
    p = "^" + re.sub("{[^}]+}", "[^/]+", tag_template)
    tag_re = p + "$|"+ p + "/.*$"
    return re.compile(tag_re).search(tag)

    
# http://2ndscale.com/rtomayko/2004/cleanest-python-find-in-list-function
def find(f, seq):
    """Return first item in sequence where f(item) == True."""
    for item in seq:
        if f(item): 
            return item
    return None


if __name__ == "__main__":
    # arg1 is MASTER_ARCHDOMAIN_TAGS archdomain.csv filename from config/config.sh.
    main(sys.argv[1])
