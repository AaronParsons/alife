#! /usr/bin/env python
"""
dna looks like:
{tag0: [[(t0,n0), (t1,n1)], [(t2,n2), (t3,n3), (t4,n4)], ...],
 tag1: [[(t5,n5)], [(t6,n6)], ...],
 ... }
"""

import random, sys, trace, threading, glob, math

# Create a list of valid python words for mutation purposes
python_words = sys.modules.keys()
for m in sys.modules:
    try: exec('import %s' % m)
    except(ImportError): continue
    python_words += eval('dir(%s)' % m)

class KThread(threading.Thread):
    """A subclass of threading.Thread, with a kill() method."""
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.setDaemon(1)
        self.killed = False
    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run # Force the Thread to install our trace.
        try: threading.Thread.start(self)
        except: pass
    def __run(self):
        """Hacked run function, which installs the trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup
    def globaltrace(self, frame, why, arg):
        if why == 'call': return self.localtrace
        else: return None
    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line': raise SystemExit()
        return self.localtrace
    def kill(self):
        self.killed = True

def flat(lst):
    """Flatten nested lists."""
    rv = []
    for L in lst:
        if type(L) == list: rv += flat(L)
        else: rv += [L]
    return rv

class DNA_Buffer:
    """Implements a buffer into which critters can insert their DNA for
    reproduction."""
    def __init__(self):
        self.buf = []
    def get(self):
        if len(self.buf) > 0: return self.buf.pop()
        else: return {}
    def put(self, dna, text):
        dna['text'] = text
        self.buf.insert(0, dna)

class Mutator(dict):
    def __init__(self, dna):
        dict.__init__(self, dna)
        self[1].append([random.choice(python_words)])
    def subkeys(self, key, key_dict=None, top=True):
        """Return a list of all keys which are referenced under key."""
        if top: key_dict = {}
        for t in self[key[0]][key[1]]:
            if type(t) == tuple:
                key_dict[t] = None
                key_dict = self.subkeys(t, key_dict=key_dict, top=False)
        if top: return key_dict.keys()
        return key_dict
    def words(self, key=(257,0)):
        """Generate a list of words generated from key, expanded out of dna."""
        val = self[key[0]][key[1]]
        for i, v in enumerate(val):
            if type(v) is tuple: val[i] = self.words(v)
        return flat(val)
    def __str__(self):
        """Add some details to self.word(s) to make a string which will run as
        a python program."""
        self[4] = [['\n']]
        self[5] = [['\t']]
        self[6] = [['\b']]
        self[0] = [['\n']]
        words = self.words()
        s = ''
        indent = ''
        for i, v in enumerate(words):
            if v == '\n': v += indent
            elif v == '\t': indent += '\t'
            elif v == '\b':
                v = ''
                indent = indent[:-1]
                s = s[:-1]
            else: v += ' '
            s += v
        self[4] = [['']]
        self[5] = [['']]
        self[6] = [['']]
        self[0] = [['']]
        return s
    def replace(self, old_key, new_key):
        """Replace every occurance of old_key with new_key."""
        for tag in self:
            for i in range(len(self[tag])):
                for j, v in enumerate(self[tag][i]):
                    if type(v) is tuple and v == old_key:
                        self[tag][i][j] = new_key
    def branch(self, old_key, new_key, scope_key=(257,0)):
        """Replace old_key with new_key within given scope_key."""
        st, sn = scope_key
        if scope_key == old_key: return new_key
        val = self[st][sn]
        new_val = val[:]
        for i, v in enumerate(new_val):
            if type(v) is tuple: new_val[i] = self.branch(old_key, new_key, v)
        if new_val != val:
            self[scope_key[0]].append(new_val)
            return (st, len(self[st])-1)
        return scope_key
    def mutate(self, mutation_rate=.1):
        """Change one (tag,num) to another over a randomly selected scope."""
        # Generate a list of keys=(tag,num) which are inside a scope
        ks = []
        while len(ks) == 0:
            # Choose scope over which mutation is to occur
            scope_tag = random.choice(self.keys())
            scope_key = (scope_tag, random.randrange(len(self[scope_tag])))
            ks = self.subkeys(scope_key)
        # Choose a random subkey which is to be replaced
        old_key = random.choice(ks)
        print 'Mutation Rate:', mutation_rate
        while random.random() < mutation_rate:
            print 'Mutating!'
            n = random.randrange(10)
            # Usually just switch keys of the same tag type
            if n != 0: new_key = self.add_value(old_key[0])
            # But occasionally, swap between tags
            else: new_key = self.add_value(random.choice(self.keys()))
            # Having selected an old key and a new one, swap them over the
            # given scope
            branch_key = self.branch(old_key, new_key, scope_key)
            self.replace(scope_key, branch_key)
    def add_value(self, tag):
        """Come up with a new value for the given tag."""
        if tag == 1: self[tag].append([random.choice(python_words)])
        v = random.choice(self[tag])[:]
        # Possibly modify v before adding it.
        while random.random() < .25:
            i = random.randrange(len(v))
            j = random.randrange(len(v))
            n = random.random()
            # Swap 2 values
            if n < .33: v[i], v[j] = v[j], v[i]
            # or insert a copy of one somewhere else
            elif n < .66: v.insert(j, v[i])
            # or delete one, as long as doing so won't eliminate all values
            elif len(v) > 1: del(v[i])
        self[tag].append(v)
        return (tag, len(self[tag])-1)

if __name__ == '__main__':
    import os, time, md5

    db = DNA_Buffer()

    def start_file(text):
        def this_thread():
            os.nice(5)
            open('tmp', 'w').write(text)
            execfile('tmp', {'mytext':text,'db':db})
        t = KThread(target=this_thread)
        t.start()
        return (t, time.time())
    
    threads = {}
    fossils = {}
    cnt = 0
    start_t = time.time()
    while True:
        # Cleanup dead critters, and enforce time limit
        for t in threads.keys():
            if not threads[t][0].isAlive(): del(threads[t])
            elif time.time() - threads[t][1] > 30:
                threads[t][0].kill()
                del(threads[t])
        # Startup new critters
        if len(threads) == 0 and len(db.buf) == 0:
            print 'Extinct.  Restarting...'
            cnt = 0
            text = open('../4.py').read()
            threads[cnt] = start_file(text)
            cnt += 1
        else:
            while len(threads) < 10 and len(db.buf) > 0:
                print len(threads), len(db.buf)
                dna = db.get()
                # Make a fossil file for future sexual reproduction
                #try: fosname = md5.new(dna['text']).hexdigest() + '.fos'
                fosname = md5.new(dna['text']).hexdigest() + '.fos'
                #except(KeyboardInterrupt): continue
                #except: continue
                if not fossils.has_key(fosname):
                    f = open(fosname, 'w'); f.write(dna['text']); f.close()
                    fossils[fosname] = None
                del(dna['text'])
                for d in dna:
                    if type(dna[d][0][0]) == str:
                        print d
                        print dna[d]
                # Possibly mutate the dna and startup the critter it makes
                # Oscillate mutation rate to alternately heat (expand variance)
                # and cool (sink into optimum solution).
                mutation_rate = .25*math.cos(.001*(time.time()-start_t)) + .25
                m = Mutator(dna)
                # Some dictionary permutations cause infinite recursion
                #try:
                #    m.mutate(mutation_rate)
                #    text = str(m)
                #except(KeyboardInterrupt): sys.exit(0)
                #except: continue
                m.mutate(mutation_rate)
                text = str(m)
                threads[cnt] = start_file(text)
                cnt += 1
            print threads.keys()
        # Limit critters-in-waiting to 300
        db.buf = db.buf[:300]    
        # Limit number of fossils to 1000
        while len(fossils) > 1000:
            f = random.choice(fossils.keys())
            os.remove(f)
            del(fossils[f])
        # Let the critters play
        time.sleep(1)
