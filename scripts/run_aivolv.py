#! /usr/bin/env python
import aivolv as ai
import hashlib, os, ctypes, threading, random, sys

MAX_CRITTERS = 1024
tempfile = 'eden/%s.py'

class Critter:
    def __init__(self, dna, tempfile=tempfile):
        self.txt = ai.dna.dna2txt(dna)
        self.my_id = hashlib.sha224(self.txt).hexdigest()[:10]
        self.filename = tempfile % self.my_id
    def _run(self):
        #sys.stdout = open(os.devnull, 'w')
        #sys.stderr = open(os.devnull, 'w')
        try:
            f = open(self.filename, 'w'); f.write(self.txt); f.close()
            env = {
                '__file__':self.filename, 
                '__name__':'__main__', 
                #'my_id':self.my_id,
            }
            execfile(self.filename, env)
        #except(RuntimeError):
        #    print 'Killed %s' % self.my_id
        except:
            print 'Died: %s' % self.my_id
    def run(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.start()
    def join(self):
        self.thread.join()
    def interrupt(self):
        if not self.thread.isAlive(): return
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(self.thread.ident), 
                ctypes.py_object(RuntimeError))
        if res > 1:
            # "if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self.thread.ident, 0)
            raise SystemError("PyThreadState_SetAsyncExc failed")
        

rx = ai.comm.DnaRx('localhost')
rx.start()
ai.eve.run(ai.eve.__file__[:-1])
print len(rx.data_buf)

critters = []
log = open('log.txt','a')
try:
    print len(rx.data_buf)
    for cnt, dna in enumerate(rx.iter_dna()):
        critters = [c for c in critters if c.thread.isAlive()]
        while len(critters) > MAX_CRITTERS:
            c = random.choice(critters)
            c.interrupt()
            c.join()
            critters = [c for c in critters if c.thread.isAlive()]
        try:
            txt = ai.dna.dna2txt(dna)
            parent_id = hashlib.sha224(txt).hexdigest()[:10]
        except(KeyError,TypeError): continue
        #ai.mutate.mutate(dna)
        if random.random() < .3:
            try: ai.mutate.mutate(dna)
            except(TypeError,KeyError): pass
        #try:
        #    if random.random() < .1: ai.mutate.mutate(dna)
        #except: pass
        try:
            c = Critter(dna)
            critters.append(c)
            c.run()
            if parent_id != c.my_id: 
                print cnt, parent_id, '->', c.my_id
                log.write('%10d %10s %10s\n' % (cnt, parent_id, c.my_id))
                log.flush()
        except: pass
        #except(SyntaxError,AttributeError,RuntimeError,TypeError): pass
        if len(rx.data_buf) == 0:
            print 'Warning: starting loop with empty buffer.'
        #except: pass
        #import IPython; IPython.embed()
except(SyntaxError):
#except(KeyboardInterrupt):
    pass
finally:
    rx.quit()
    log.close()
