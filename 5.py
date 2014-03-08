#! /usr/bin/env python
import ast, socket, cPickle, random

def addtagval(dna, tag, val):
    if not dna.has_key(tag):
        dna[tag] = [val]
        return (tag, 0)
    try: return (tag, dna[tag].index(val))
    except(ValueError):
        dna[tag].append(val)
        return (tag, len(dna[tag])-1)

def ast2dna(n, dna, indent=''):
    tag = type(n).__name__
    #print indent, tag
    indent += '   '
    if not isinstance(n, ast.AST): return addtagval(dna, tag, n)
    val = {}
    for field,_val in ast.iter_fields(n):
        #print indent, field, _val
        if type(_val) == list: val[field] = [ast2dna(v, dna=dna, indent=indent) for v in _val]
        else: val[field] = ast2dna(_val, dna=dna, indent=indent)
    #print indent, tag, val
    return addtagval(dna, tag, val)
        

def dna2ast(tag, num, dna, indent=''):
    print indent, tag, num, dna[tag][num]
    val = dna[tag][num]
    indent += '   '
    if type(val) == dict:
        rv = eval('ast.%s()' % tag)
        for k in val:
            print indent, k, val[k]
            if type(val[k]) == list: _val = [dna2ast(v[0],v[1], dna, indent=indent) for v in val[k]]
            else: _val = dna2ast(val[k][0], val[k][1], dna, indent=indent)
            print indent, k, _val
            setattr(rv, k, _val)
        rv.lineno = 0
        rv.col_offset = 0
    else: rv = val
    return rv
    
        
a = ast.parse(open('5.py').read())
dna = {}
ast2dna(a, dna)
#print '='*70
#print dna['Load']
#print '='*70
a = dna2ast('Module',0,dna)
#print '='*70
#exec(compile(a, '<string>', 'exec'))

