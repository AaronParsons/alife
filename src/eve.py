import aivolv

def run():
    a = ast.parse(open(__file__).read())
    dna = {}
    aivolv.dna.ast2dna(a, dna)
    tx = aivolv.comm.DnaTx('localhost')
    tx.send_dna(dna)

if __name__ == '__main__':
    run() 
