#! /usr/bin/env python
import sys, string, keyword, random
from dparser import Parser, Reject

def flat(lst):
    rv = []
    for L in lst:
        if type(L) == list: rv += flat(L)
        else: rv += [L]
    return rv

class Vocabulary(dict):
    nospacers = ['identifier', 'literal']
    multidents = ['if_stmt', 'try_exc_stmt', 'try_fin_stmt', 'for_stmt', 
        'while_stmt']
    def add(self, tag, val):
        self[tag] = self.get(tag, [{}, {}])
        i = len(self[tag][0].keys())
        s = str(val)
        self[tag][0][s] = self[tag][0].get(s, i)
        if self[tag][0][s] == i: self[tag][1][i] = val
        return (tag, self[tag][0][s])
    def expand(self, tag, num, spacer=' ', indent=''):
        if tag in self.nospacers: spacer = ''
        elif tag == 'NEWLINE': return '\n' + indent
        elif tag == 'indent_suite': indent += '    '
        def f(x):
            if type(x) == str: return x
            return self.expand(x[0], x[1], spacer, indent)
        rv = [f(x) for x in self[tag][1][num] if x != None]
        if tag == 'indent_suite':
            rv = [indent + r for r in rv]
            rv = [r.rstrip() + '\n' for r in rv]
            rv = spacer.join(rv)
            return rv.rstrip() + '\n'
        elif tag in self.multidents:
            for i, r in enumerate(rv):
                if r in ['else', 'elif', 'except', 'finally']: 
                    rv[i] = indent + r
        elif tag == 'file_input': spacer = ''
        rv = spacer.join(rv)
        if tag == 'suite': return rv.rstrip() + '\n'
        else: return rv
    def sub_keys(self, tag, num):
        rv = {}
        for t in self[tag][1][num]:
            if type(t) == tuple:
                rv[t] = 0
                for r in self.sub_keys(t[0], t[1]): rv[r] = 0
        return rv.keys()
    def mutate(self, grammar, scope_tag=None, scope_num=None, tag=None, orig_num=None, new_num=None, top=1):
        if scope_tag == None:
            sk = []
            while sk == []:
                scope_tag = random.choice(self.keys())
                scope_num = random.choice(self[scope_tag][1].keys())
                sk = self.sub_keys(scope_tag, scope_num)
            tag, orig_num = random.choice(sk)
            if random.randrange(2): new_num = grammar.babble(tag, voc)[1]
            else: new_num = random.choice(self[tag][1].keys())
        if scope_tag == tag and scope_num == orig_num: return (tag, new_num)
        else:
            rv = []
            for i in self[scope_tag][1][scope_num]:
                if i is None: pass
                elif type(i) == str: rv += [i]
                else: rv += [self.mutate(grammar, i[0], i[1], tag, orig_num, new_num, 0)]
            if top: self[scope_tag][1][scope_num] = rv
            else: return self.add(scope_tag, rv)

class Grammar(dict):
    nsp = """if spec:
        b = this.buf; i = this.start_loc.s; j = this.end
        words = b[i:j].split()
        mytxt = words[0]
        if len(words) > 1 and not words[1].startswith('#'): return Reject
        id_str = string.letters + string.digits + '_'
        if i > 0 and b[i-1] in id_str: return Reject
        if (j < len(b) and b[j] in id_str) and b[j-1] in id_str: return Reject
        if mytxt in keyword.kwlist: return Reject
        return 1"""
    ljn = """global linejoin
    linejoin += 1
    if spec: return 1"""
    luj = """global linejoin
    linejoin = max([linejoin-1, 0])
    if spec: return 1"""
    stg = """global instr
    instr.add_token(name, this.start_loc.s)
    if spec: return 1"""
    mid = """if spec:
        indent = get_indent(this.buf, this.start_loc.s, this.end)
        lines = this.buf[this.start_loc.s:this.end].splitlines()
        for L in lines[1:]:
            Ls = L.lstrip()
            i = len(L) - len(Ls)
            if len(Ls) == 0: pass
            elif i < indent: return Reject
            elif i == indent:
                flag = 1
                for w in ['else', 'elif', 'except', 'finally']:
                    if L.lstrip().startswith(w): flag = 0
                if flag: return Reject
        return 1"""
    nospec_func = """def d_%s(t):
    r''' %s : %s '''
    name = '%s'
    return voc.add(name, flat(t))"""
    func = """def d_%s(t, spec, this):
    r''' %s : %s '''
    name = '%s'
    %s
    return voc.add(name, flat(t))"""
    indent_func = """def d_%s(t, spec, this):
    r''' %s : %s '''
    name = '%s'
    if spec:
        indent = get_indent(this.buf, this.start_loc.s, this.end)
        for s in this.c:
            nextindent = get_indent(this.buf, s.start_loc.s + 1, this.end)
            if nextindent >= 0 and nextindent <= indent:
                return Reject
        finalindent = get_indent(this.buf, this.end + 1, len(this.buf) - 1)
        if finalindent > indent:
            return Reject
        return 1
    return voc.add(name, flat(t))"""
    def make_grammar(self):
        rv = []
        for tag in self:
            if tag in ['identifier', 'integer','longinteger','floatnumber', 'imagnumber']:
                rv += [self.func % (tag, tag, self.get_str(tag), tag, self.nsp)]
            elif tag in ['LP', 'LB', 'LC']:
                rv += [self.func % (tag, tag, self.get_str(tag), tag, self.ljn)]
            elif tag in ['RP', 'RB', 'RC']:
                rv += [self.func % (tag, tag, self.get_str(tag), tag, self.luj)]
            elif tag in ['SQ', 'DQ', 'TSQ', 'TDQ']:
                rv += [self.func % (tag, tag, self.get_str(tag), tag, self.stg)]
            elif tag in ['if_stmt', 'try_exc_stmt', 'try_fin_stmt', 'for_stmt', 'while_stmt']:
                rv += [self.func % (tag, tag, self.get_str(tag), tag, self.mid)]
            elif tag == 'indent_suite':
                rv += [self.indent_func % (tag, tag, self.get_str(tag), tag)]
            else:
                rv += [self.nospec_func % (tag, tag, self.get_str(tag), tag)]
        return rv
    def get_str(self, tag):
        rv = []
        if type(tag) == str: lst = self[tag]
        else: lst = tag
        for L in lst:
            if type(L) == str: rv += [L]
            else: rv += ['(', self.get_str(L), ')']
        return ' '.join(rv)
    def get_grammar_strings(self):
        rv = ['%s : %s' % (tag, self.get_str(tag)) for tag in self]
        rv.sort()
        return '\n'.join(rv)
    def babble(self, item, voc):
        if type(item) == str:
            if item.startswith("'"): rv = item[1:-1]
            elif item.startswith('"'):
                i = item.find('['); j = i + item[i:].find(']') + 1
                if i != -1:
                    rv = eval('"' + item[1:i] + '"')
                    if item[i:j].startswith('[^'):
                        mlist = list(string.printable)
                        for L in self.expand(item[i+2:j-1]):
                            try: mlist.remove(L)
                            except(ValueError): pass
                        rv += random.choice(mlist)
                    else: rv += random.choice(self.expand(item[i+1:j-1]))
                else: rv = eval('"' + item[1:-1] + '"')
            else:
                if item in voc.keys() and random.randrange(2): 
                    rv = (item, random.choice(voc[item][1].keys()))
                else:
                    rv = voc.add(item, flat(self.babble(self[item], voc)))
        elif type(item) == list:
            options = [[]]
            i = 0
            for t in item:
                if t != '|': options[i] += [t]
                else:
                    options += [[]]
                    i += 1
            o = random.choice(options)
            s = []
            i = 0
            while i < len(o):
                if i+1 < len(o):
                    if o[i+1] == '?':
                        if random.randrange(2): s += [self.babble(o[i], voc)]
                        i += 2
                    elif o[i+1] == '*':
                        if random.randrange(2):
                            s += [self.babble(o[i], voc)]
                        else: i += 2
                    elif o[i+1] == '+':
                        s += [self.babble(o[i], voc)]
                        s += [self.babble([o[i], '*'], voc)]
                        i += 2
                    else:
                        s += [self.babble(o[i], voc)]
                        i += 1
                else:
                    s += [self.babble(o[i], voc)]
                    i += 1
            rv = s
        return rv
    def expand(self, s):
        rv = ''
        i = 0
        while i < len(s):
            if s[i] == '\\':
                i += 2
                c = eval('"' + s[i-2:i] + '"')
            else:
                i += 1
                c = s[i-1:i]
            if i < len(s) and s[i] == '-':
                i += 1
                if s[i] == '\\':
                    i += 2
                    d = eval('"' + s[i-2:i] + '"')
                else:
                    i += 1
                    d = s[i-1:i]
                a = string.printable.find(c)
                b = string.printable.find(d) + 1
                rv += string.printable[a:b]
            else: rv += c
        return rv

g = Grammar({
'LP':["'('"],
'RP':["')'"],
'LB':["'['"],
'RB':["']'"],
'LC':["'{'"],
'RC':["'}'"],
'SQ':['''"'"'''],
'DQ':["""'"'"""],
'TSQ':[r"'\'\'\''"],
'TDQ':[''''"""' '''],
'NEWLINE':[r"'\n'"],
'C':["','"],
'identifier':['"[a-zA-Z_]"','"[a-zA-Z0-9_]"','*'],
'stringliteral':['stringprefix','?',['shortstring','|','longstring']],
'stringprefix':["'r'",'|',"'u'",'|',"'ur'",'|',"'R'",'|',"'U'",'|',"'UR'",'|',
    "'Ur'",'|',"'uR'"],
'shortstring':['SQ',[r'"[^\\\n\']"','|','escapeseq'],'*','SQ','|','DQ',
    [r'"[^\\\n\"]"','|','escapeseq'],'*','DQ'],
'longstring':['TSQ',[r'"[^\\\']"','|','SQ',r'"[^\\\']"','|','SQ','SQ',
    r'"[^\\\']"','|','escapeseq'],'*','TSQ','|','TDQ',[r'"[^\\\"]"','|',
    'DQ',r'"[^\\\"]"','|','DQ','DQ',r'"[^\\\"]"','|','escapeseq'],'*','TDQ'],
'escapeseq':[r'"\\[^]"'],
'longinteger':['integer',["'l'",'|',"'L'"]],
'integer':['decimalinteger','|','octinteger','|','hexinteger'],
'decimalinteger':['"[1-9]"','"[0-9]"','*','|',"'0'"],
'octinteger':["'0'",'"[0-7]"','+'],
'hexinteger':["'0'",["'x'",'|',"'X'"],'"[0-9a-fA-F]"','+'],
'floatnumber':['pointfloat','|','exponentfloat'],
'pointfloat':['intpart','?','fraction','|','intpart',"'.'"],
'exponentfloat':[['intpart','|','pointfloat'],'exponent'],
'intpart':['"[0-9]"','+'],
'fraction':["'.'",'"[0-9]"','+'],
'exponent':[["'e'",'|',"'E'"],["'+'",'|',"'-'"],'?','"[0-9]"','+'],
'imagnumber':[['floatnumber','|','intpart'],["'j'",'|',"'J'"]],
'atom':['identifier','|','literal','|','enclosure'],
'literal':['stringliteral','|','integer','|','longinteger','|','floatnumber',
    '|','imagnumber'],
'enclosure':['parenth_form','|','list_display','|',
    'parenth_generator_expression','|','list_generator_expression','|',
    'dict_display','|','string_conversion'],
'dict_display':['LC',['expression',"':'",'expression',['C','expression',"':'",
    'expression'],'*','C','?'],'?','RC'],
'string_conversion':["'`'",'expression_list',"'`'"],
'parenth_generator_expression':['LP','expression','genexpr_for','RP'],
'list_generator_expression':['LB','expression','genexpr_for','RB'],
'genexpr_iter':['genexpr_for','|','genexpr_if'],
'genexpr_for':["'for'",'expression_list',"'in'",'expression','genexpr_iter',
    '?'],
'genexpr_if':["'if'",'expression','genexpr_iter','?'],
'list_display':['LB','expression_list','?','RB'],
'parenth_form':['LP','expression_list','?','RP'],
'expression_list':['expression',['C','expression'],'*','C','?'],
'expression':['or_test','|','lambda_form'],
'or_test':['and_test','|','or_test',"'or'",'and_test'],
'and_test':['not_test','|','and_test',"'and'",'not_test'],
'not_test':['comparison','|',"'not'",'not_test'],
'comparison':['or_expr',['comp_operator','or_expr'],'*'],
'comp_operator':["'<'",'|',"'>'",'|',"'=='",'|',"'>='",'|',"'<='",'|',"'<>'",
    '|',"'!='",'|',"'is'","'not'",'?','|',"'not'",'?',"'in'"],
'or_expr':['xor_expr','|','or_expr',"'|'",'xor_expr'],
'xor_expr':['and_expr','|','xor_expr',"'^'",'and_expr'],
'and_expr':['shift_expr','|','and_expr',"'&'",'shift_expr'],
'shift_expr':['a_expr','|','shift_expr',["'<<'",'|',"'>>'"],'a_expr'],
'a_expr':['m_expr','|','a_expr',"'+'",'m_expr','|','a_expr',"'-'",'m_expr'],
'm_expr':['u_expr','|','m_expr',"'*'",'u_expr','|','m_expr',"'//'",'u_expr','|','m_expr',"'/'",'u_expr','|','m_expr',"'%'",'u_expr'],
'u_expr':['power','|',"'-'",'u_expr','|',"'+'",'u_expr','|',"'~'",'u_expr'],
'power':['primary',["'**'",'u_expr'],'?'],
'primary':['atom','|','attributeref','|','subscription','|','slicing','|',
    'call'],
'attributeref':['primary',"'.'",'identifier'],
'subscription':['primary','LB','expression_list','RB'],
'slicing':['simple_slicing','|','extended_slicing'],
'simple_slicing':['primary','LB','short_slice','RB'],
'extended_slicing':['primary','LB','slice_list','RB'],
'slice_list':['slice_item',['C','slice_item'],'*','C','?'],
'slice_item':['expression','|','proper_slice','|','ellipsis'],
'proper_slice':['short_slice','|','long_slice'],
'short_slice':['lower_bound','?',"':'",'upper_bound','?'],
'long_slice':['short_slice',"':'",'stride','?'],
'lower_bound':['expression'],
'upper_bound':['expression'],
'stride':['expression'],
'ellipsis':["'...'"],
'call':['primary','LP',['argument_list','C','?'],'?','RP'],
'argument_list':['positional_arguments',['C','keyword_arguments'],'?',
    ['C',"'*'",'expression'],'?',['C',"'**'",'expression'],'?','|',
    'keyword_arguments',['C',"'*'",'expression'],'?',['C',"'**'",
    'expression'],'?','|',"'*'",'expression',['C',"'**'",'expression'],'?',
    '|',"'**'",'expression'],
'positional_arguments':['expression',['C','expression'],'*'],
'keyword_arguments':['keyword_item',['C','keyword_item'],'*'],
'keyword_item':['identifier',"'='",'expression'],
'parameter_list':[['defparameter','C'],'*',["'*'",'identifier',['C',"'**'",
    'identifier'],'?','|',"'**'",'identifier'],'|','defparameter',['C',
    'defparameter'],'*','C','?'],
'defparameter':['parameter',["'='",'expression'],'?'],
'sublist':['parameter',['C','parameter'],'*','C','?'],
'parameter':['identifier','|','LP','sublist','RP'],
'lambda_form':["'lambda'",'parameter_list','?',"':'",'expression'],
'simple_stmt':['expression_stmt','|','assert_stmt','|','assignment_stmt','|',
    'augmented_assignment_stmt','|','pass_stmt','|','del_stmt','|',
    'print_stmt','|','return_stmt','|','yield_stmt','|','raise_stmt','|',
    'break_stmt','|','continue_stmt','|','import_stmt','|','global_stmt','|',
    'exec_stmt'],
'expression_stmt':['expression_list'],
'assert_stmt':["'assert'",'expression',['C','expression'],'?'],
'assignment_stmt':[['target_list',"'='"],'+','expression_list'],
'target_list':['target',['C','target'],'*','C','?'],
'target':['identifier','|','LP','target_list','RP','|','LB','target_list','RB',
    '|','attributeref','|','subscription','|','slicing'],
'augmented_assignment_stmt':['target','augop','expression_list'],
'augop':["'+='",'|',"'-='",'|',"'*='",'|',"'/='",'|',"'%='",'|',"'**='",'|',
    "'>>='",'|',"'<<='",'|',"'&='",'|',"'^='",'|',"'|='"],
'pass_stmt':["'pass'"],
'del_stmt':["'del'",'target_list'],
'print_stmt':["'print'",[['expression',['C','expression'],'*','C','?'],'?',
    '|',"'>>'",'expression',['C','expression'],'+','C','?']],
'return_stmt':["'return'",'expression_list','?'],
'yield_stmt':["'yield'",'expression_list'],
'raise_stmt':["'raise'",['expression',['C','expression',['C','expression'],
    '?'],'?'],'?'],
'break_stmt':["'break'"],
'continue_stmt':["'continue'"],
'import_stmt':["'import'",'module',["'as'",'identifier'],'?',['C','module',
    ["'as'",'identifier'],'?',],'*','|',"'from'",'module',"'import'",
    'identifier',["'as'",'identifier'],'?',['C','identifier',["'as'",
    'identifier'],'?',],'*','|',"'from'",'module',"'import'",'LP','identifier',
    ["'as'",'identifier'],'?',['C','identifier',["'as'",'identifier'],'?',],
    '*','C','?','RP','|',"'from'",'module',"'import'","'*'"],
'module':[['identifier',"'.'"],'*','identifier'],
'global_stmt':["'global'",'identifier',['C','identifier'],'*'],
'exec_stmt':["'exec'",'expression',["'in'",'expression',['C','expression'],
    '?'],'?'],
'stmt_list':['simple_stmt',["';'",'simple_stmt'],'*',"';'",'?'],
'compound_stmt':['if_stmt','|','while_stmt','|','for_stmt','|','try_stmt','|',
    'funcdef','|','classdef'],
'statement':['stmt_list','NEWLINE','+','|','compound_stmt'],
'suite':['statement','|','indent_suite'],
'try_stmt':['try_exc_stmt','|','try_fin_stmt'],
'classdef':["'class'",'classname','inheritance','?',"':'",'suite'],
'inheritance':['LP','expression_list','RP'],
'classname':['identifier'],
'funcdef':['decorators','?',"'def'",'funcname','LP','parameter_list','?','RP',
    "':'",'suite'],
'decorators':['decorator','+'],
'decorator':["'@'",'identifier',["'.'",'identifier'],'*',['LP',
    ['argument_list','C','?'],'?','RP'],'?','NEWLINE'],
'funcname':['identifier'],
'file_input':[['NEWLINE','|','statement'],'*'],
'if_stmt':["'if'",'expression',"':'",'suite',["'elif'",'expression',"':'",
    'suite'],'*',["'else'","':'",'suite'],'?'],
'while_stmt':["'while'",'expression',"':'",'suite',["'else'","':'",'suite'],
    '?'],
'for_stmt':["'for'",'target_list',"'in'",'expression_list',"':'",'suite',
    ["'else'","':'",'suite'],'?'],
'try_exc_stmt':["'try'","':'",'suite',["'except'",['expression',['C',
    'target'],'?'],'?',"':'",'suite'],'+',["'else'","':'",'suite'],'?'],
'try_fin_stmt':["'try'","':'",'suite',"'finally'","':'",'suite'],
'indent_suite':['NEWLINE','+','statement','+'],
})

def get_indent(buf, start, end):
    if start >= len(buf): return -1
    i = start
    while i > 0 and buf[i-1] != '\n': i -= 1
    lines = buf[i:end].splitlines()
    if len(lines) == 0: return -1
    line = lines[0]
    line_lstrip = line.lstrip()
    if len(line_lstrip) == 0 or line_lstrip.startswith('#'): return -1
    return len(line) - len(line_lstrip)

class InString:
    td = {'':'', 'SQ':"'", 'DQ':'"', 'TSQ':"'''", 'TDQ':'"""'}
    toks = ['', '']
    locs = [-2, -1]
    def instring(self, loc):
        i = len(self.locs) - 1
        while i >= 0 and self.locs[i] > loc: i -= 1
        return (i + 1) % 2
    def add_token(self, t, loc):
        while loc <= self.locs[-1]:
            self.locs = self.locs[:-1]
            self.toks = self.toks[:-1]
        if loc >= self.locs[-1] + len(self.td[t]) and (len(self.toks) % 2 == 0 or t == self.toks[-1]):
            self.locs += [loc]
            self.toks += [t]
    def cur_tok_val(self):
        return self.toks[-1], self.td[self.toks[-1]]

def d_whitespace(t, spec, this):
    r''' whitespace : "[ \t\n]"+ | '#' "[^\n]"* '''
    global instr, linejoin
    if spec:
        if instr.instring(this.start_loc.s):
            ct, cv = instr.cur_tok_val()
            if this.buf[this.start_loc.s-1-len(cv):this.start_loc.s-1] == cv and this.buf[this.start_loc.s-2-len(cv)] != '\\':
                instr.add_token(ct, this.start_loc.s-1-len(cv))
            if this.buf[this.start_loc.s-len(cv):this.start_loc.s] == cv:
                instr.add_token(ct, this.start_loc.s-len(cv))
        else:
            if this.buf[this.start_loc.s-1] == '"':
                instr.add_token('DQ', this.start_loc.s-1)
            elif this.buf[this.start_loc.s-1] == "'":
                instr.add_token('SQ', this.start_loc.s-1)
            if this.buf[this.start_loc.s] == '"':
                instr.add_token('DQ', this.start_loc.s)
            elif this.buf[this.start_loc.s] == "'":
                instr.add_token('SQ', this.start_loc.s)
        real_linejoin = linejoin > 1 or (linejoin == 1 and this.buf[this.start_loc.s-1] not in '])}') or (linejoin == 0 and this.buf[this.start_loc.s-1] in '[{(')
        if not real_linejoin and '\n' in this.buf[this.start_loc.s:this.end]:
            return Reject
        if instr.instring(this.start_loc.s): return Reject
        return 1
voc = Vocabulary()
txt = open(__file__).read()
for s in g.make_grammar(): exec(s)
indent = [0]
linejoin = 0
instr = InString()
Parser().parse(txt, start_symbol='file_input', commit_actions_interval=len(txt))
voc.mutate(g)
print '#! /usr/bin/env python\n' + voc.expand('file_input', 0).strip() + '\n'
