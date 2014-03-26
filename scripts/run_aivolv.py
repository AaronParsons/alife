#! /usr/bin/env python
import aivolv as ai
import random
import multiprocessing, multiprocessing.queues
from multiprocessing import Process, Queue, Lock, Value
import multiprocessing.queues
import os 
import signal

MAX_QUEUE_LEN = 100
MAX_CRITTERS = 512
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
    def __init__(self, name, max_critters=MAX_CRITTERS, max_qlen=MAX_QUEUE_LEN):
        self.name = name
        self._quit = multiprocessing.Event()
        self.max = max_critters
        self.dna_q = Queue(max_qlen) # important to limit Queue size to avoid memory overrun
        self.thread = None
        self.critters = []
        self.purgatory = []
    def send_dna(self, d):
        #logit(self.name + 'queuing')
        self.dna_q.put_nowait(d)
    def _run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        while not self._quit.is_set():
            try: d = self.dna_q.get_nowait()
            except(multiprocessing.queues.Empty): continue
            cntit()
            cnt = get_cnt()
            self.critters = self.clean(self.critters, self.max)
            try: pid = ai.critter.hashtxt(ai.dna.dna2txt(d))
            except(KeyError,TypeError): continue
            if random.random() < .5:
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
            self.purgatory.append(c)
            #c.join()
            critters = [c for c in critters if c.is_alive()]
        self.purgatory = [c for c in self.purgatory if c.thread.is_alive()]
        return critters
    def is_alive(self):
        if not self.thread is None: return self.thread.is_alive()
        else: return False
    def run(self):
        self._quit.clear()
        self.thread = Process(target=self._run)
        self.thread.start()
    def stop(self):
        self._quit.set()
        self.clean(self.critters, 0)
        self.dna_q.close()
    def terminate(self):
        if not self.thread is None: self.thread.terminate()
    def join(self, timeout=None):
        if not self.thread is None: self.thread.join(timeout)
        self.thread = None
        

rx = ai.comm.DnaRx('localhost')
rx.start()
ai.eve.run(ai.eve.__file__[:-1])
print len(rx.data_buf)

bios = [BioSphere('bio%02d'%i) for i in range(NUM_BIOS)]
for b in bios: b.run()

i = 0
try:
    for dna in rx.iter_dna():
        #logit('Sending one to bio%02d' % (i%NUM_BIOS))
        i = (i + 1) % NUM_BIOS
        if not bios[i].is_alive():
            bios[i] = BioSphere('bio%02d'%i)
            logit('# Remaking ' + bios[i].name )
            bios[i].run()
        try:
            bios[i].send_dna(dna) 
        except(multiprocessing.queues.Full):
            #logit('# bio%02d is full' % 1)
            pass
        if random.random() < .0001:
            logit('# Destroying ' + b.name )
            b = random.choice(bios)
            b.stop()
            b.join()
            #b.terminate()
        #if len(rx.data_buf) == 0:
        #    logit('Warning: starting loop with empty buffer.')
    #import IPython; IPython.embed()
#except(SyntaxError):
except(KeyboardInterrupt):
    pass
finally:
    for b in bios: b.stop()
    for b in bios: b.join()
    rx.stop()
    #log_lock.release()
    #cnt_lock.release()
    #log.close()
    #import IPython; IPython.embed()


