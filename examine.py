#! /usr/bin/env python
import os, sys

startfile = '../d4120caf92bd81ca8c5b6e286874762b.fos'
normal = {}
for L in open(startfile).readlines(): normal[L] = None

mutate = {}
for a in sys.argv[1:]:
    print a,
    lines = open(a).readlines()
    rv = []
    for L in lines:
        if normal.has_key(L): continue
        if mutate.has_key(L):
            mutate[L][1] += 1
            rv.append(mutate[L][0])
        else:
            rv.append(len(mutate))
            mutate[L] = [len(mutate), 1]
    rv.sort()
    print rv

def sort_keys(x, y):
    if mutate[x][1] > mutate[y][1]: return 1
    return -1

keys = mutate.keys()
keys.sort(sort_keys)
for m in keys:
    print mutate[m], m.strip()
