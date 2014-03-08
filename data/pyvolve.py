#! /usr/bin/env python
import ast, socket, random, threading, cPickle, sys, time

def dna2ast(tag, num, dna, indent=''):
    #print indent, tag, num, dna[tag][num]
    val = dna[tag][num]
    indent += '   '
    if type(val) == dict:
        rv = eval('ast.%s()' % tag)
        for k in val:
            #print indent, k, val[k]
            if type(val[k]) == list:
                _val = [dna2ast(v[0],v[1], dna, indent=indent) for v in val[k]]
            else:
                _val = dna2ast(val[k][0], val[k][1], dna, indent=indent)
            #print indent, k, _val
            setattr(rv, k, _val)
        rv.lineno = 0
        rv.col_offset = 0
    else: rv = val
    return rv

class CritterThread(threading.Thread):
    def __init__(self, a, critterlock, master_port):
        self.code = compile(a, '<string>', 'exec')
        def f(): exec self.code in {'myast':a, 'master_port':master_port}
        threading.Thread.__init__(self, target=f)
        self.daemon = 1
        self.killed = False
        self.critterlock = critterlock
    def start(self):
        self.__run_backup = self.run
        self.run = self._run
        self.critterlock.acquire()
        threading.Thread.start(self)
    def _run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup
    def globaltrace(self, frame, event, arg):
        if event == 'call': return self.localtrace
        else: return None
    def localtrace(self, frame, event, arg):
        self.critterlock.release()
        if self.killed:
            if event == 'line': raise SystemExit()
        self.critterlock.acquire()
        return self.localtrace
    def kill(self):
        self.killed = True

class MasterServer:
    def __init__(self, port, monitor):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.settimeout(.1)
        self._sock.bind(('', port))
        self.monitor = monitor
    def read(self, buf={}):
        try:
            data, addr = self._sock.recvfrom(8192)
            cmd, id, nparts, i, d = cPickle.loads(data)
            if not buf.has_key(id): buf[id] = (cmd, [''] * nparts)
            buf[id][1][i] = d
            #print 'Master: Got data %d/%d (len=%d) from %s' % (i, nparts, len(d), addr)
            #for x in buf[id][1]: print len(x),
            #print 
            if i + 1 == nparts: return (buf[id][0], ''.join(buf[id][1]))
            else: return self.read(buf=buf)
        except(cPickle.UnpicklingError,socket.timeout): return ('NOOP', '')
    def start(self):
        self._quit = False
        self.thread = threading.Thread(target=self._rx)
        self.thread.daemon = 1
        self.thread.start()
    def _rx(self):
        while not self._quit:
            #print 'RX alive'
            cmd,data = self.read()
            #print 'Master:', cmd, len(data)
            if cmd == 'PUTNEW':
                #print 'Master: got PUTNEW'
                try:
                    dna = cPickle.loads(data)
                    a = dna2ast('Module', 0, dna)
                    self.monitor.add_critter(a)
                    print 'Master: PUTNEW succeeded'
                #except(cPickle.UnpicklingError, AttributeError):
                except:
                    print 'Master: PUTNEW unpack failed'
            time.sleep(.01)
    def stop(self):
        self._quit = True
        self.thread.join()

class Monitor:
    def __init__(self, ncritters, maxpop, master_port):
        self.maxpop = maxpop
        self.critterlock = threading.Semaphore(ncritters)
        self.critters = {}
        self.master_port = master_port
    def add_critter(self, a):
        #print 'Adding critter'
        self.cull(self.maxpop-1)
        c = CritterThread(a, self.critterlock, self.master_port)
        for i in xrange(self.maxpop):
            if self.critters.has_key(i): continue
            self.critters[i] = c
            print 'Critter %d: started' % i
            self.critters[i].start()
            break
        #print 'Exiting add_critter'
    def cull(self, maxpop=None):
        #print 'Culling'
        if maxpop is None: maxpop = self.maxpop
        # Get rid of any critters already done
        for i in self.critters.keys():
            if not self.critters[i].is_alive():
                print 'Critter %d: already ended' % i
                del(self.critters[i])
        # If there are still too many, get rid of some more
        while len(self.critters) > maxpop:
            i = random.choice(self.critters.keys())
            self.critters[i].kill()
            #print 'Joining critter %d' % i
            self.critters[i].join()
            del(self.critters[i])
            print 'Critter %d: culled (%d remaining)' % (i, len(self.critters))
        #print 'Exiting cull'
    def end(self):
        self.cull(0)
        

if __name__ == '__main__':
    PORT = 18000
    NCRITTERS = 10
    MAXPOP = 30

    monitor = Monitor(NCRITTERS, MAXPOP, PORT)
    ms = MasterServer(PORT, monitor)
    ms.start()
    for filename in sys.argv[1:]:
        print 'Reading critter from', filename
        a = ast.parse(open(filename).read())
        monitor.add_critter(a)
    try:
        while True:
            print 'Update:', threading.active_count(), ms.thread.is_alive()
            time.sleep(1)
    except(KeyboardInterrupt): pass
    ms.stop()
    monitor.end()
            
