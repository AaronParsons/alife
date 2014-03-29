#! /usr/bin/env python
import alife as ai
import random
import multiprocessing as mp
import multiprocessing.queues as mpq

NUM_BIOS = 10

logging_q = mp.Queue()
log = open('log.txt','a')
def logit(s, verbose=True):
    if verbose: print s
    log.write(s + '\n')
    log.flush()

rx = ai.comm.DnaRx('localhost')
rx.start()
ai.eve.run(ai.eve.__file__[:-1])
print len(rx.data_buf)

bios = [ai.bio.BioSphere('bio%02d'%i, logging_q) for i in range(NUM_BIOS)]
for b in bios: b.run()

cnt = 0
i = 0
try:
    for dna in rx.iter_dna():
        #logit('Sending one to bio%02d' % (i%NUM_BIOS))
        while not logging_q.empty():
            bname,pid,cid = logging_q.get()
            logit('%10s %10d %10s %10s' % (bname, cnt, pid, cid))
            cnt += 1
        i = (i + 1) % NUM_BIOS
        if not bios[i].is_alive():
            bios[i] = ai.bio.BioSphere('bio%02d'%i, logging_q)
            logit('# Remaking ' + bios[i].name )
            bios[i].run()
        try:
            bios[i].send_dna(dna) 
        except(mpq.Full):
            #logit('# bio%02d is full' % 1)
            pass
        #if random.random() < .0001:
        if False:
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
    #for b in bios: b.join()
    rx.stop()
    logging_q.close()
    #log_lock.release()
    #cnt_lock.release()
    #log.close()
    #import IPython; IPython.embed()


