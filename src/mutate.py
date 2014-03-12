import random, copy

def mutate(dna):
    return copy.deepcopy(dna)
    #k = random.choice(dna.keys())
    #i1 = random.randrange(0, len(dna[k]))
    ##print k, i1, dna[k][i1]
    #i2 = random.randrange(0, len(dna[k]))
    #print k, i1, i2, dna[k][i1], dna[k][i2]
    #dna[k][i1],dna[k][i2] = dna[k][i2],dna[k][i1]


