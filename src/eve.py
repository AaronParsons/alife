#import dna, comm
import aivolv as ai
import ast

if not globals().has_key('my_id'): my_id = 'eve'

def run():
    f = __file__
    if f.endswith('pyc'): f = f[:-1]
    #print f
    txt = open(f).read()
    a = ast.parse(txt)
    d = {'my_id':my_id}
    #import IPython; IPython.embed()
    ai.dna.ast2dna(a, d)
    tx = ai.comm.DnaTx('localhost')
    tx.send_dna(d)
    tx.send_dna(d)

if __name__ == '__main__':
    run() 
