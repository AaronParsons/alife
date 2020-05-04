from .critter import hashtxt, Critter
from .mutate import mutate
import multiprocessing as mp
import multiprocessing.queues as mpq
import random, signal


MAX_QUEUE_LEN = 100
MAX_CRITTERS = 512
#MAX_CRITTERS = 5

class BioSphere:
    '''A BioSphere is a process in charge of running the threads of
    multiple Critters. If a critter destabilizes a process, it brings
    down a BioSphere without destroying the whole program.'''
    def __init__(self, name, logging_q, max_critters=MAX_CRITTERS, 
            max_qlen=MAX_QUEUE_LEN):
        self.name = name
        self.logging_q = logging_q
        self._quit = mp.Event()
        self.max = max_critters
        # limit Queue size to avoid memory overrun
        self.dna_q = mp.Queue(max_qlen)
        self.thread = None
        self.critters = []
        self.purgatory = []

    def send_dna(self, d):
        '''Insert DNA into the processing queue.'''
        self.dna_q.put_nowait(d)

    def _run(self):
        '''Endless loop of processing new DNA (with mutation).'''
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        while not self._quit.is_set():
            try:
                dna = self.dna_q.get_nowait()
            except(mpq.Empty):
                continue
            self.critters = self.clean(self.critters, self.max)
            try:
                pid = hashtxt(dna.to_txt())
            except(KeyError,TypeError):
                continue
            if random.random() < .5:
            #if False:
                try:
                    mutate(dna)
                except(TypeError,KeyError):
                    pass
            try:
                c = Critter(dna)
                c.run() # must precede append, otherwise not threadsafe
                self.critters.append(c)
                if pid != c.my_id:
                    self.logging_q.put((self.name, pid, c.my_id))
            except:
                pass

    def clean(self, critters, maxcrit):
        '''Remove terminated Critters and cull if over maximum size.'''
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
        '''Check that BioSphere itself is still alive.'''
        if self.thread is not None:
            return self.thread.is_alive()
        else:
            return False

    def run(self):
        '''Begin running this BioSphere.'''
        self._quit.clear()
        self.thread = mp.Process(target=self._run)
        #self.thread.daemon = True
        self.thread.start()

    def stop(self):
        '''Shut down this BioSphere and all critters inside it.'''
        self._quit.set()
        self.clean(self.critters, 0)
        self.dna_q.close()

    def terminate(self):
        '''Terminate BioSphere process.'''
        if self.thread is not None:
            self.thread.terminate()

    def join(self, timeout=None):
        '''Join with BioSphere process.'''
        if self.thread is not None:
            self.thread.join(timeout)
        self.thread = None

    def __del__(self):
        self.stop()
