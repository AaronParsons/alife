#! /usr/bin/env python
import numpy as n, pylab as plt
import sys

def get_log_data(logfile):
    #d = n.loadtxt(logfile, dtype={'names': ('bio', 'time', 'pid', 'cid'), 'formats': ('S10', 'i4', 'S10', 'S10')})
    #d = n.loadtxt(logfile, dtype={'names': ('pid', 'cid'), 'formats': ('S10', 'S10')}, usecols=(2,3))
    d = n.array([L.split()[2:] for L in open(logfile).readlines()])
    return d

print 'Reading', sys.argv[-1]
d = get_log_data(sys.argv[-1])

print 'linking...'
ids, id_list = {}, []
kid2pid,pid2kid = {}, {}
#for t,pid,cid  in zip(d['time'], d['pid'],d['cid']):
for t,(pid,kid) in enumerate(d):
    if not ids.has_key(pid):
        ids[pid] = [t,t]
        id_list.append(pid)
    else: ids[pid][-1] = t
    kid2pid[kid] = pid
for k in kid2pid.keys():
    if not ids.has_key(k): del(kid2pid[k])
for k in kid2pid.keys():
    p = kid2pid[k]
    pid2kid[p] = pid2kid.get(p,[]) + [k]

done = {}
def nest(pid2kid, p):
    global done
    if done.has_key(p) or (not pid2kid.has_key(p)): return {p:[]}
    done[p] = None
    return {p: [nest(pid2kid,k) for k in pid2kid[p]]}

tree = []
for i in id_list:
    if done.has_key(i): continue
    tree.append(nest(pid2kid,i))
    
print tree[0]
def flatten(tree):
    rv = []
    for d in tree:
        for k in d.keys():
            rv.append(k)
            rv += flatten(d[k])
    return rv

sorted_id_list = flatten(tree)

print len(id_list), len(sorted_id_list)

print 'plotting...'
for c,i in enumerate(sorted_id_list):
    plt.plot(ids[i],[c,c], 'k-')
#for id1 in cid2pid:
#    id0 = cid2pid[id1]
#    (t1,c1),(t0,c0) = ids[id1], ids[id0]
#    t2 = lasttime[id1]
#    #p.plot([t0,t1,t2],[c0,c1,c1], 'k-', alpha=.5)
#    p.plot([t1,t2],[c1,c1], 'k-', alpha=.5)

plt.show()
    
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
