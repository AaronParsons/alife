#! /usr/bin/env python
'''This script reads in a log.txt file and removes all files
from the directory 'eden' that did not generate an entry in log.txt'''
import numpy as n
import sys, os

tempfile = 'eden/%s.py'

def get_log_data(logfile):
    d = n.array([L.split()[2:] for L in open(logfile).readlines() if not L.startswith('#')])
    return d

print('Reading', sys.argv[-1])
d = get_log_data(sys.argv[-1])

ids = {}
kid2pid = {}

for pid,kid in d:
    ids[pid] = None
    kid2pid[kid] = pid
for k in kid2pid.keys():
    if not ids.has_key(k):
        if os.path.exists(tempfile % k):
            #print 'Removing', tempfile % k
             os.remove(tempfile % k)
