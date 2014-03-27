import dna, critter, mutate
import multiprocessing as mp
import multiprocessing.queues as mpq
import random, signal


MAX_QUEUE_LEN = 100
MAX_CRITTERS = 512
#MAX_CRITTERS = 5

class BioSphere:
    def __init__(self, name, logging_q, max_critters=MAX_CRITTERS, max_qlen=MAX_QUEUE_LEN):
        self.name = name
        self.logging_q = logging_q
        self._quit = mp.Event()
        self.max = max_critters
        self.dna_q = mp.Queue(max_qlen) # important to limit Queue size to avoid memory overrun
        self.thread = None
        self.critters = []
        self.purgatory = []
    def send_dna(self, d):
        self.dna_q.put_nowait(d)
    def _run(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        while not self._quit.is_set():
            try: d = self.dna_q.get_nowait()
            except(mpq.Empty): continue
            self.critters = self.clean(self.critters, self.max)
            try: pid = critter.hashtxt(dna.dna2txt(d))
            except(KeyError,TypeError): continue
            if random.random() < .5:
            #if False:
                try: mutate.mutate(d)
                except(TypeError,KeyError): pass
            try:
                c = critter.Critter(d)
                self.critters.append(c)
                c.run()
                if pid != c.my_id:
                    self.logging_q.put((self.name, pid, c.my_id))
            except: pass
    def clean(self, critters, maxcrit):
        critters = [c for c in critters if c.is_alive()]
        while len(critters) > self.max:
            #print 'cleaning', len(critters), len(self.purgatory)
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
        self.thread = mp.Process(target=self._run)
        #self.thread.daemon = True
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
    def __del__(self):
        self.stop()
