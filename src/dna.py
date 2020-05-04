import ast, astunparse
import marshal

MAX_RECUR = 100

class DNA:
    '''DNA has the following structure:
    {k0: [i0, i1, ...], k1:[i0, i1, ...], ...}
    where each item i can be 
    1) a primitive (str,int,float,...),
    2) a (k,n) pair, where k is a dna key and n is an integer, or
    3) a list of (k,n) pairs.'''

    def __init__(self, txt=None, pkt=None, dna_dict=None, 
                 ast_parse_tree=None):
        self._dna = {}
        if ast_parse_tree is not None:
            self.from_ast(ast_parse_tree)
        elif txt is not None:
            self.from_txt(txt)
        elif pkt is not None:
            self.deserialize(pkt)
        elif dna_dict is not None:
            self._dna = dna_dict

    def __getitem__(self, key):
        return self._dna[key]

    def __setitem__(self, key, val):
        self._dna[key] = val

    def keys(self):
        return list(self._dna.keys())

    def add_tagval(self, tag, val):
        '''Add a new tag/val pair to DNA, if not there already.'''
        if tag not in self._dna:
            self._dna[tag] = [val]
            return (tag, 0)
        try:
            return (tag, self._dna[tag].index(val))
        except(ValueError):
            self._dna[tag].append(val)
            return (tag, len(self._dna[tag]) - 1)

    def from_ast(self, n, recur=0):
        '''Build a DNA object from an AST parse tree.'''
        if recur > MAX_RECUR:
            raise RuntimeError('Exceeded recursion depth of %d' % recur)
        tag = type(n).__name__
        if not isinstance(n, ast.AST) and recur > 0:
            return self.add_tagval(tag, n)
        val = []
        for field,_val in ast.iter_fields(n):
            if type(_val) is list:
                _val = [self.from_ast(v, recur=recur+1) for v in _val]
            else:
                _val = self.from_ast(_val, recur=recur+1)
            val.append(self.add_tagval(field, _val))
        return self.add_tagval(tag, val)

    def to_ast(self, tag='Module', num=0, recur=0):
        '''Build an AST parse tree from a DNA object.'''
        if recur > MAX_RECUR:
            raise RuntimeError('Exceeded recursion depth of %d' % recur)
        val = self._dna[tag][num]
        if type(val) is list:
            rv = eval('ast.%s()' % tag)
            for k,i in val:
                if type(self._dna[k][i]) is list:
                    _val = [self.to_ast(v[0],v[1], recur=recur+1)
                            for v in self._dna[k][i]]
                else:
                    _val = self.to_ast(k, i, recur=recur+1)
                setattr(rv, k, _val)
            rv.lineno = 0
            rv.col_offset = 0
        elif type(val) is tuple:
            rv = self.to_ast(val[0], val[1], recur=recur+1)
        else:
            rv = val
        return rv

    def to_txt(self, tag='Module', num=0):
        '''Build a string representation of a DNA object, starting
        at the specified tag/val pair.'''
        ast_parse_tree = self.to_ast(tag=tag, num=num)
        return astunparse.unparse(ast_parse_tree)

    def from_txt(self, txt):
        '''Parse DNA object from text.'''
        ast_parse_tree = ast.parse(txt)
        self.from_ast(ast_parse_tree)

    def serialize(self):
        '''Convert into a bytes object that can be transmitted.'''
        return marshal.dumps(self._dna)

    def deserialize(self, pkt):
        '''Reconstruct DNA from a bytes object created with serialize().'''
        self._dna = marshal.loads(pkt)

