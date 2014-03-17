import random, copy, dna

def random_pair(dna, k=None):
    if k is None: k = random.choice(dna.keys())
    while len(dna[k]) == 0: k = random.choice(dna.keys())
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
    ks,ns = random_pair(d)
    #ks,ns = 'Module',0
    #ks,ns = 'FunctionDef',0
    if ks == 'my_id': return
    subks = subkeys(d,ks,ns)
    pair1 = random.choice(subks)
    #pair1 = ('str',1)
    #pair1 = ('body',4)
    if random.random() < .5:
    #if random.random() < 0:
        pair2 = random_pair(d)
    else:
        k,n = pair1
        item = babble(d, k, n)
        #print k, d[k][n]
        #print k, item
        #d[k][n] = item
        d[k].append(item)
        pair2 = (k,len(d[k])-1)
        #print d[pair2[0]][pair2[1]]
    #ks,ns = random_pair(d)
    #print ks, ns, pair1, pair2, len(d[k])
    #print '>', d[k]
    d[ks][ns] = swap(d, pair1, pair2, ks, ns)
    #print d[ks][ns]
    #import unparse, StringIO
    #a = dna.dna2ast(d)
    #f = StringIO.StringIO()
    #unparse.Unparser(a, f)
    #txt = f.getvalue(); f.close()
    #print txt
    #import IPython; IPython.embed()

def swap(d,pair1,pair2,k,n):
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
            item.insert(random.randrange(len(item)+1), random_pair(d))
        return item 
    elif type(item) is tuple:
        return random_pair(d)
    elif type(item) is str:
        new_item = random.choice(dna.ast_map.keys())
        if random.random() < .5:
            new_item = list(new_item)
            random.shuffle(new_item)
            new_item = ''.join(new_item)
        return new_item
    elif type(item) is int:
        return random.randrange(-10,10)
    else:
        return random.choice(d[k])
    
        
