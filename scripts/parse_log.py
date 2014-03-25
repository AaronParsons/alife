#! /usr/bin/env python
import numpy as n, pylab as p
import sys

LOG_DTYPE = n.dtype([('bio', n.str_, 10), ('time',n.int32), ('pid', n.str_, 10), ('cid', n.str_, 10)])

def get_log_data(logfile):
    d = n.loadtxt(logfile, dtype={'names': ('bio', 'time', 'pid', 'cid'), 'formats': ('S10', 'i4', 'S10', 'S10')})
    return d

d = get_log_data(sys.argv[-1])

# cull to only ids that produced progeny
ids = {}
lasttime = {}
cid2pid = {}
for t,pid,cid  in zip(d['time'], d['pid'],d['cid']):
    cid2pid[cid] = pid
    ids[pid] = ids.get(pid,(t,len(ids))) # keep the earliest time this pid appeared
    lasttime[pid] = t
for k in cid2pid.keys():
    if not ids.has_key(k): del(cid2pid[k])

def back_prop(ids, k):
    try: pk = cid2pid[k]
    except(KeyError): return
    t,c = ids[k]
    pt,pc = ids[pk]
    mpc = max(c,pc)
    if mpc != pc:
        ids[pk] = (pt,mpc)
        back_prop(ids, pk)
    

print len(ids)
#for k in ids:
for k in ids: back_prop(ids, k)

for id1 in cid2pid:
    id0 = cid2pid[id1]
    (t1,c1),(t0,c0) = ids[id1], ids[id0]
    t2 = lasttime[id1]
    p.plot([t0,t1,t2],[c0,c1,c1], 'k-', alpha=.5)

p.show()
    
#eves = {}
#for i, pid in enumerate(d['pid']):
#    try: pids[pid] = cid2pid[pid]
#    except(KeyError): eves[pid] = eves.get(pid,i)
#cid2pid = pids
#
#tree = {}
#for i in cid2pid.keys():
#    try:
#        pid = cid2pid[i]
#        tree[pid] = tree.get(pid,[]) + [i]
#    except(KeyError): pass

#import IPython; IPython.embed()
