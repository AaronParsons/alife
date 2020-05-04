import random, copy
from . import dna

def random_pair(dna, k=None):
    if k is None: k = random.choice(list(dna.keys()))
    while len(dna[k]) == 0: k = random.choice(list(dna.keys()))
    return (k, random.randrange(len(dna[k])))

def subkeys(dna, k, n):
    rv = [(k,n)]
    item = dna[k][n]
    if type(item) is list:
        for _k,_n in item: rv += subkeys(dna,_k,_n)
    elif type(item) is tuple:
        rv += subkeys(dna,item[0],item[1])
    return rv    

def mutate(d):
    #return 
    if random.random() < .5:
        ks,ns = 'Module',0
    else:
        ks,ns = random_pair(d)
    subks = subkeys(d,ks,ns)
    if random.random() < .5: pair1 = random_pair(d, 'body')
    else: pair1 = random.choice(subks)
    if random.random() < .5:
        pair2 = random_pair(d)
    else:
        k,n = pair1
        item = babble(d, k, n)
        d[k].append(item)
        pair2 = (k,len(d[k])-1)
    #d[ks][ns] = swap(d, pair1, pair2, ks, ns)
    k,n = swap(d, pair1, pair2, ks, ns)
    d[ks][ns] = d[k][n] 

def swap(d,pair1,pair2,k,n):
    if (k,n) == pair1: return pair2
    item = d[k][n]
    if type(item) is list:
        new_item = [swap(d,pair1,pair2,_k,_n) for _k,_n in item]
        d[k].append(new_item)
        return (k,len(d[k])-1)
    elif type(item) is tuple:
        _k,_n = item
        if item == pair1: # another base case
            d[k].append(pair2)
        else:
            d[k].append(swap(d,pair1,pair2,_k,_n)) 
        return (k,len(d[k])-1)
    else: # base case
        return (k,n)

def babble(d, k, n):
    item = d[k][n]
    if type(item) is list:
        item = item[:]
        if len(item) > 0 and random.random() < .5:
            item.pop(random.randrange(len(item)))
        else:
            if len(item) == 0 or random.random() < .5: item.insert(random.randrange(len(item)+1), random_pair(d))
            else:
                if random.random() < .5: item.insert(random.randrange(len(item)+1), random.choice(item))
                else: random.shuffle(item)
        return item 
    elif type(item) is tuple:
        return random_pair(d)
    elif type(item) is str:
        if random.random() < .5:
            new_item = random.choice(list(dna.ast_map.keys()))
        else:
            new_item = random.choice(d['str'])
        #if random.random() < .5:
        #    new_item = list(new_item)
        #    random.shuffle(new_item)
        #    new_item = ''.join(new_item)
        return new_item
    elif type(item) is int:
        return random.randrange(-10,10)
    else:
        return random.choice(d[k])
    
        
