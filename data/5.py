import ast, random, socket, cPickle, math

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
    indent += '   '
    if not isinstance(n, ast.AST): return addtagval(dna, tag, n)
    val = {}
    for field,_val in ast.iter_fields(n):
        if type(_val) == list: val[field] = [ast2dna(v, dna=dna, indent=indent) for v in _val]
        else: val[field] = ast2dna(_val, dna=dna, indent=indent)
    return addtagval(dna, tag, val)

def mixdna(mydna, urdna):
    for tag in urdna:
        if random.randrange(2):
            urdna[tag] = mydna[tag]
    return urdna

class TxSocket:
    def __init__(self, ip, port, maxsize=4096):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._ip_port = (ip, port)
        self.maxsize = maxsize
    def write(self, cmd, data):
        id = random.random()
        d = cPickle.dumps(data)
        nparts = int(math.ceil(float(len(d)) / self.maxsize))
        #print 'Critter:', len(d), nparts
        for i in range(nparts):
            _d = cPickle.dumps((cmd, id, nparts, i, d[:self.maxsize]))
            self._sock.sendto(_d, self._ip_port)
            d = d[self.maxsize:]

class Critter:
    def __init__(self, mydna, rx_port, master_tx):
        self.mydna = mydna
        self.rx_port = rx_port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.settimeout(.1)
        self._sock.bind(('',self.rx_port))
        self.master = master_tx
    def read(self, buf={}):
        try:
            data,addr = self._sock.recvfrom(8192)
            cmd, id, nparts, i, d = cPickle.loads(data)
            if not buf.has_key(id): buf[id] = (cmd, [''] * nparts)
            buf[id][1][i] = d
            if i + 1 == nparts: return(buf[id][0], ''.join(buf[id][1]))
            else: return self.read(buf=buf)
        except(cPickle.UnpicklingError, socket.timeout): return ('NOOP', '')
    def react(self):
        state = 'PUTDNA'
        while True:
            #print 'Critter (port=%d):' % self.rx_port, state
            if state == 'PUTDNA':
                tx_port = self.rx_port + random.randint(-5,5)
                #print 'Critter (port=%d,state=%s): sending dna to %d' % (self.rx_port, state, tx_port)
                dna_sock = TxSocket('localhost', tx_port)
                dna_sock.write('PUTDNA', self.mydna)
                state = 'GETDNA'
            elif state == 'GETDNA':
                cmd, data = self.read()
                if cmd == 'PUTDNA':
                    try:
                        urdna = cPickle.loads(data)
                        newdna = mixdna(self.mydna, urdna)
                        print 'Critter (port=%d,state=%s): got dna and is reproducing' % (self.rx_port, state)
                        self.master.write('PUTNEW', newdna)
                    except(cPickle.UnpicklingError): pass
                    #self.master.write('PUTNEW', self.mydna)
                state = 'PUTDNA'
    
IP = 'localhost'
MYPORT = master_port + random.randint(0,1000)

mydna = {}
ast2dna(myast, mydna) # myast is provided by the master in the global env
master_tx = TxSocket(IP, master_port) # master_port is also provided in global env
me = Critter(mydna, MYPORT, master_tx)
me.react()
