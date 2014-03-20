#! /usr/bin/env python
import aivolv as ai
import random
from multiprocessing import Process, Queue, Lock, Value

MAX_CRITTERS = 1024
NUM_BIOS = 10

log = open('log.txt','a')
log_lock = Lock()
def logit(s, verbose=True):
    log_lock.acquire()
    if verbose: print s
    log.write(s + '\n')
    log.flush()
    log_lock.release()

cnt = Value('i',0)
cnt_lock = Lock()
def cntit():
    cnt_lock.acquire()
    cnt.value += 1
    cnt_lock.release()
def get_cnt():
    return cnt.value

class BioSphere:
    def __init__(self, name, max_critters=MAX_CRITTERS):
        self.name = name
        self.max = max_critters
        self.dna_q = Queue()
        self.thread = None
        self.critters = []
    def send_dna(self, d):
        #logit(self.name + 'queuing')
        self.dna_q.put(d)
    def _run(self):
        while True:
            #logit(self.name+ 'waiting on queue')
            d = self.dna_q.get()
            #logit(self.name+ 'got one')
            cntit()
            cnt = get_cnt()
            self.critters = self.clean(self.critters, self.max)
            if d == 'end':
                self.critters = self.clean(self.critters, 0) # destroy all active critters
                break
            try: pid = ai.critter.hashtxt(ai.dna.dna2txt(d))
            except(KeyError,TypeError): continue
            if random.random() < .3:
                try: ai.mutate.mutate(d)
                except(TypeError,KeyError): pass
            try:
                c = ai.critter.Critter(d)
                self.critters.append(c)
                c.run()
                if pid != c.my_id: 
                    logit('%10s %10d %10s %10s' % (self.name, cnt, pid, c.my_id))
            except: pass
    def clean(self, critters, maxcrit):
        critters = [c for c in critters if c.is_alive()]
        while len(critters) > self.max:
            c = random.choice(critters)
            c.interrupt()
            c.join()
            critters = [c for c in critters if c.is_alive()]
        return critters
    def run(self):
        self.thread = Process(target=self._run)
        self.thread.start()
    def stop(self):
        self.dna_q.put('end')
    def join(self):
        if not self.thread is None: self.thread.join()
        self.thread = None
        

rx = ai.comm.DnaRx('localhost')
rx.start()
ai.eve.run(ai.eve.__file__[:-1])
print len(rx.data_buf)

bios = [BioSphere('bio%02d'%i) for i in range(NUM_BIOS)]
for b in bios: b.run()

try:
    for i,dna in enumerate(rx.iter_dna()):
        #logit('Sending one to bio%02d' % (i%NUM_BIOS))
        bios[i % NUM_BIOS].send_dna(dna)
        #if len(rx.data_buf) == 0:
        #    logit('Warning: starting loop with empty buffer.')
#except(SyntaxError):
except(KeyboardInterrupt):
    pass
finally:
    for b in bios: b.stop()
    rx.quit()
    log.close()
for b in bios: 
    b.thread.terminate()
    b.join()
