#!/usr/bin/env python

from __future__ import print_function

def split_group_name(label):
    m = {
        '-usw1-prod': 'usw1-prod',
        '-prod': 'prod',
        '-canary': 'canary',
        '-stage': 'stage',
        '-dev': 'dev',
        '-phnx': 'phnx'
    }
    env='unknown'
    if label is not None:
        for k,v in m.items():
            if label.endswith(k):
                label,env = (label.split(k)[0], v)
                break
    if label.endswith('-docker'):
        label = label[:-len('-docker')]
    return label,env
