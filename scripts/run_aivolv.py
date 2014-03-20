#! /usr/bin/env python
import aivolv as ai
import random

MAX_CRITTERS = 1024

rx = ai.comm.DnaRx('localhost')
rx.start()
ai.eve.run(ai.eve.__file__[:-1])
print len(rx.data_buf)

critters = []
log = open('log.txt','a')

def logit(s, verbose=True):
    if verbose: print s
    log.write(s + '\n')
    log.flush()

try:
    print len(rx.data_buf)
    for cnt, dna in enumerate(rx.iter_dna()):
        critters = [c for c in critters if c.is_alive()]
        while len(critters) > MAX_CRITTERS:
            c = random.choice(critters)
            c.interrupt()
            c.join()
            critters = [c for c in critters if c.is_alive()]
        try:
            parent_id = ai.critter.hashtxt(ai.dna.dna2txt(dna))
        except(KeyError,TypeError): continue
        #ai.mutate.mutate(dna)
        if random.random() < .3:
            try: ai.mutate.mutate(dna)
            except(TypeError,KeyError): pass
        try:
            c = ai.critter.Critter(dna)
            critters.append(c)
            c.run()
            if parent_id != c.my_id: 
                logit('%10d %10s %10s' % (cnt, parent_id, c.my_id))
        except: pass
        #except(SyntaxError,AttributeError,RuntimeError,TypeError): pass
        if len(rx.data_buf) == 0:
            print 'Warning: starting loop with empty buffer.'
        #import IPython; IPython.embed()
#except(SyntaxError):
except(KeyboardInterrupt):
    pass
finally:
    rx.quit()
    log.close()
