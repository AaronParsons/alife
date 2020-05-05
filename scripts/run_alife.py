#! /usr/bin/env python
import alife as ai
#import aivolv as ai
import random
import multiprocessing as mp
import multiprocessing.queues as mpq

def tail(f, lines=100, bufsize=1024):
    total_lines_wanted = lines

    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - bufsize > 0):
            f.seek(block_number*bufsize, 2)
            blocks.append(f.read(bufsize))
        else:
            f.seek(0,0)
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count(b'\n')
        lines_to_go -= lines_found
        block_end_byte -= bufsize
        block_number -= 1
    all_read_text = b''.join(reversed(blocks))
    return all_read_text.splitlines()[-total_lines_wanted:]

NUM_BIOS = 10

logging_q = mp.Queue()
log = open('log.txt','a')
def logit(s, verbose=True):
    if verbose: print(s)
    log.write(s + '\n')
    log.flush()

rx = ai.comm.DnaRx('localhost')
rx.start()
if False: # start alife with the original 'eve' critter
    ai.eve.run(ai.eve.__file__)
else: # restart where alife terminated with the last N entries in the log
    log_tmp = open('log.txt','rb')
    seed_critters = [L.split() for L in tail(log_tmp)]
    seed_critters = [L[2].decode('utf-8') for L in seed_critters 
                     if len(L) > 3]
    log_tmp.close()
    for i in range(10):
        crit = random.choice(seed_critters)
        logit('# Seeding %s' % crit)
        ai.eve.run('eden/%s.py' % crit)

print(len(rx.data_buf))

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
        if len(rx.data_buf) == 0:
            #logit('Warning: starting loop with empty buffer.')
            pass
    #import IPython; IPython.embed()
#except(SyntaxError):
except(KeyboardInterrupt):
    pass
finally:
    for b in bios: 
        print('Stopping', b.name, b.is_alive(), len(b.critters), len(b.purgatory), b.dna_q.full())
        for c in b.critters: print(c.my_id)
        b.stop()
    #for b in bios: b.join()
    rx.stop()
    logging_q.close()
    #log_lock.release()
    #cnt_lock.release()
    #log.close()
    import IPython; IPython.embed()


