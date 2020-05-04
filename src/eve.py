import alife as ai
import ast
import time

#if not globals().has_key('my_id'): my_id = 'eve'

def run(f=__file__):
    #f = __file__
    #if f.endswith('pyc'): f = f[:-1]
    #print f
    dna = ai.dna.DNA(txt=open(f).read())
    tx = ai.comm.DnaTx('localhost')
    tx.send_dna(dna)
    tx.send_dna(dna)
    time.sleep(1)

if __name__ == '__main__':
    run() 
