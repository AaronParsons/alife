import ast

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

def dna2ast(dna, tag='Module', num=0, recur=0):
    #print indent, tag, num, dna[tag][num]
    val = dna[tag][num]
    #indent = '   ' * recur
    if type(val) is list:
        rv = eval('ast.%s()' % tag)
        for k,i in val:
            #print indent, tag, k, dna[k][i]
            if type(dna[k][i]) == list: _val = [dna2ast(dna, v[0],v[1], recur=recur+1) for v in dna[k][i]]
            else: _val = dna2ast(dna, k, i, recur=recur+1)
            setattr(rv, k, _val)
        rv.lineno = 0
        rv.col_offset = 0
    elif type(val) is tuple:
        rv = dna2ast(dna, val[0], val[1], recur=recur+1)
    else:
        rv = val
    return rv

