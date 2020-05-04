#! /usr/bin/env python
'''Display graphically the evolutionary history descirbed in a log.txt file.'''

import numpy as n, pylab as plt
import sys

img = n.zeros((8192,512), dtype=n.int)

def get_log_data(logfile):
    #d = n.loadtxt(logfile, dtype={'names': ('bio', 'time', 'pid', 'cid'), 'formats': ('S10', 'i4', 'S10', 'S10')})
    #d = n.loadtxt(logfile, dtype={'names': ('pid', 'cid'), 'formats': ('S10', 'S10')}, usecols=(2,3))
    d = [L.split() for L in open(logfile).readlines() if not L.startswith('#')]
    d = n.array([L[2:] for L in d if len(L) > 3])
    return d

print('Reading', sys.argv[-1])
d = get_log_data(sys.argv[-1])

print('linking...')
max_ids = {None:0}
ids, id_list = {None:img.shape[1]/2}, []
kid2pid,pid2kid = {}, {}
orphans = {}
#for t,pid,cid  in zip(d['time'], d['pid'],d['cid']):
parent = None
tmax = 0
for t,(pid,kid) in enumerate(d):
    if t < tmax: t += tmax
    else: tmax = t
    x = t / 1000
    if not ids.has_key(pid):
        if not kid2pid.has_key(pid): # this is an orphan
            orphans[pid] = None
            # parent will default to the previous parent, for current lack of a better option
        else:
            parent = kid2pid[pid]
        next_id = -max_ids[parent]
        if next_id >= 0: next_id += 1
        max_ids[parent] = next_id
        ids[pid] = next_id + ids[parent]
        max_ids[pid] = 0
    y = ids[pid] % img.shape[1]
    #if orphans.has_key(pid):
    img[x,y] += 1
    kid2pid[kid] = pid

#plt.imshow(img, cmap='gist_yarg', interpolation='nearest', origin='lower', aspect='auto')
plt.imshow(n.log10(img), cmap='Paired', interpolation='nearest', origin='lower', aspect='auto')
#for pid,t in orphans:
#    x = t / 1000
#    y = ids[pid] % img.shape[1]
#    plt.plot([y],[x],'r.')
plt.show()

#for k in kid2pid.keys():
#    if not ids.has_key(k): del(kid2pid[k])
#for k in kid2pid.keys():
#    p = kid2pid[k]
#    pid2kid[p] = pid2kid.get(p,[]) + [k]
#
#done = {}
#def nest(pid2kid, p):
#    global done
#    if done.has_key(p) or (not pid2kid.has_key(p)): return {p:[]}
#    done[p] = None
#    return {p: [nest(pid2kid,k) for k in pid2kid[p]]}
#
#tree = []
#for i in id_list:
#    if done.has_key(i): continue
#    tree.append(nest(pid2kid,i))
#
#def prune(t,k=None, new_tree=[]):
#    new_t = []
#    for i,d in enumerate(t):
#        new_d = {}
#        for k1 in d.keys():
#            new_d[k1] = prune(d[k1],k1)
#        new_t.append(d)
#    if len(new_t) == 0:
#        return [k]
#    if len(new_t) == 1:
#        return new_t[0].values()
#    else:
#        return new_t
#    
##tree = prune(tree)
#
##print len(tree)
##print [t.keys()[0] for t in tree]
#
#def flatten(tree):
#    rv = []
#    for d in tree:
#        if not type(d) == dict:
#            print tree
#            print d
#        for k in d.keys():
#            rv.append(k)
#            rv += flatten(d[k])
#    return rv
#
#sorted_id_list = flatten(tree)
#
#print len(id_list), len(sorted_id_list)

#for c,i in enumerate(sorted_id_list):
#    plt.plot(ids[i],[c,c], 'k-')
#for id1 in cid2pid:
#    id0 = cid2pid[id1]
#    (t1,c1),(t0,c0) = ids[id1], ids[id0]
#    t2 = lasttime[id1]
#    #p.plot([t0,t1,t2],[c0,c1,c1], 'k-', alpha=.5)
#    p.plot([t1,t2],[c1,c1], 'k-', alpha=.5)

    
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
