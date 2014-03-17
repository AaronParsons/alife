#! /usr/bin/env python
import aivolv
import ast
import hashlib, copy
import unparse, StringIO

def addtagval(dna, tag, val):
    if not dna.has_key(tag):
        dna[tag] = [val]
        return (tag, 0)
    try: return (tag, dna[tag].index(val))
    except(ValueError):
        dna[tag].append(val)
        return (tag, len(dna[tag])-1)

def ast2dna(n, dna, recur=0):
    tag = type(n).__name__
    indent = '   ' * recur
    if not isinstance(n, ast.AST): return addtagval(dna, tag, n)
    val = []
    for field,_val in ast.iter_fields(n):
        if type(_val) is list: 
            _val = [ast2dna(v, dna=dna, recur=recur+1) for v in _val]
        else: _val = ast2dna(_val, dna=dna, recur=recur+1)
        val.append(addtagval(dna, field, _val))
    return addtagval(dna, tag, val)
        
a = ast.parse(open(__file__).read())
#f = StringIO.StringIO()
#unparse.Unparser(a, f)
#myhash = hashlib.sha224(f.getvalue()).hexdigest()
#f.close()
#print 'Me:', myhash
dna = {}
ast2dna(a, dna)
tx = aivolv.comm.DnaTx('localhost')
tx.send_dna(dna)
#new_dna = copy.deepcopy(dna)
#mutate(new_dna)
#new_a = dna2ast('Module', 0, new_dna)
#f = StringIO.StringIO()
#unparse.Unparser(new_a, f)
#txt = f.getvalue(); f.close()
#new_hash = hashlib.sha224(txt).hexdigest()
#print myhash[:10], '->', new_hash[:10]
##import IPython; IPython.embed()
#if myhash != new_hash:
#    print txt
##    #print '='*70
##    try:
#exec(compile(new_a, '<string>', 'exec'))
##    except: continue

