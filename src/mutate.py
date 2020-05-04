import random, copy

# provide a map of available built-in AST structures to draw on for
# mutation.
AST_MAP = {}
for i,k in enumerate(__builtins__.keys()):
    AST_MAP[k] = i

def random_pair(dna, k=None):
    '''Select a random key/val pair from DNA.'''
    if k is None:
        k = random.choice(dna.keys())
    while len(dna[k]) == 0:
        k = random.choice(dna.keys())
    return (k, random.randrange(len(dna[k])))

def subkeys(dna, k, n):
    '''Find (k,n) and all of its children in dna.'''
    rv = [(k,n)]
    item = dna[k][n]
    if type(item) is list:
        for _k,_n in item:
            rv += subkeys(dna,_k,_n)
    elif type(item) is tuple:
        rv += subkeys(dna,item[0],item[1])
    return rv    

def mutate(dna):
    '''Modify a DNA object by rewiring it or introducing new structure.'''
    #return 
    if random.random() < .5:
        ks,ns = 'Module',0
    else:
        ks,ns = random_pair(dna)
    subks = subkeys(dna, ks, ns)
    if random.random() < .5:
        pair1 = random_pair(dna, 'body')
    else:
        pair1 = random.choice(subks)
    if random.random() < .5:
        pair2 = random_pair(dna)
    else:
        k,n = pair1
        item = babble(dna, k, n)
        dna[k].append(item)
        pair2 = (k, len(dna[k]) - 1)
    k,n = swap(dna, pair1, pair2, ks, ns)
    dna[ks][ns] = dna[k][n] 

def swap(dna, pair1, pair2, k, n):
    '''Swap the usage of two key/val pairs in a DNA object.'''
    if (k,n) == pair1:
        return pair2
    item = dna[k][n]
    if type(item) is list:
        new_item = [swap(dna, pair1, pair2, _k, _n) for _k,_n in item]
        dna[k].append(new_item)
        return (k, len(dna[k]) - 1)
    elif type(item) is tuple:
        _k,_n = item
        if item == pair1: # another base case
            dna[k].append(pair2)
        else:
            dna[k].append(swap(dna, pair1, pair2, _k, _n)) 
        return (k,len(dna[k])-1)
    else: # base case
        return (k,n)

def babble(dna, k, n):
    '''Babble out some new DNA structure.'''
    item = dna[k][n]
    if type(item) is list:
        item = item[:]
        if len(item) > 0 and random.random() < .5:
            item.pop(random.randrange(len(item)))
        else:
            if len(item) == 0 or random.random() < .5:
                item.insert(random.randrange(len(item)+1), random_pair(dna))
            else:
                if random.random() < .5:
                    item.insert(random.randrange(len(item)+1), 
                                random.choice(item))
                else:
                    random.shuffle(item)
        return item 
    elif type(item) is tuple:
        return random_pair(dna)
    elif type(item) is str:
        if random.random() < .5:
            new_item = random.choice(list(AST_MAP.keys()))
        else:
            new_item = random.choice(dna['str'])
        #if random.random() < .5:
        #    new_item = list(new_item)
        #    random.shuffle(new_item)
        #    new_item = ''.join(new_item)
        return new_item
    elif type(item) is int:
        return random.randrange(-10, 10)
    else:
        return random.choice(dna[k])
    
