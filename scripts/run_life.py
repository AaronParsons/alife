#! /usr/bin/env python

import os, sys, time, glob, string, cPickle, gzip
import critter, webstuff

if len(sys.argv) > 1 and sys.argv[1] == '-v':
    import visuals, Tkinter, Pmw
    root = Tkinter.Tk()
    Pmw.initialise(root)
    visuals = visuals.PyvolveGraph(root)
    visuals.show()
else:
    visuals = None

rt = '..'

# FILES
evolog = rt + '/evolog.gz'
halt = rt + '/halt.txt'
state = rt + '/run_life.st'
crit = ['3.py', '2.py']
globcrit = '*.py'

# PARAMETERS
time_out = 60
max_time = 520
max_file_num = 128
iter = 10

downloader = None
uploader = None

def should_quit():
    if visuals: return os.path.exists(halt) or not visuals.go
    else: return os.path.exists(halt)

def should_upload():
    if visuals: return visuals.upload
    return 0

def should_break():
    return should_quit() or should_upload()
        
def evologit(txt):
    if type(txt) == list: t = ' '.join(map(str, txt)) + '\n'
    elif type(txt) == str: t = txt + '\n'
    f = gzip.open(evolog, 'a'); f.write(t); f.close()
    if visuals: visuals.add_text(t)

def download():
    global downloader
    downloader = webstuff.Downloader(rt + '/download.tmp')
    evologit('Downloading...')
    downloader.start()
    while downloader.isAlive() and not should_quit(): time.sleep(1)

def are_different(file1, file2):
    f = open(file1); d1 = f.read(); f.close()
    f = open(file2); d2 = f.read(); f.close()
    return d1.split() != d2.split()

def is_valid(file):
    try: return os.stat(file)[6] > 2000
    except(OSError): return 0

def upload():
    global uploader
    uploader = webstuff.Uploader(rt + '/upload.tmp', glob.glob(globcrit))
    evologit('Uploading ...')
    uploader.start()
    while uploader.isAlive() and not should_quit(): time.sleep(1)

def get_growth_rate(filenum):
    if filenum > max_file_num: return 1
    elif filenum > max_file_num / 4: return 13
    return 26

def exit(cur_iter):
    if downloader != None and downloader.isAlive():
        downloader.halt()
    if uploader != None and uploader.isAlive():
        uploader.halt()
    f = open(state, 'wb')
    cPickle.dump(cur_iter, f)
    f.close()

asciis = string.ascii_letters + string.digits
os.chdir('eden')

while 1:
    if os.path.exists(state):
        f = open(state, 'rb')
        cur_iter = cPickle.load(f)
        f.close()
    else: cur_iter = 0
    if len(glob.glob(globcrit)) == 0:
        download()
        cur_iter = 0
    for i in range(cur_iter, iter):
        evologit(["Beginning iteration", i, '/', iter])
        # Get rid of any empty files ahead of time.
        map(os.remove, [f for f in glob.glob(globcrit) if os.stat(f).st_size == 0])
        critters = glob.glob(globcrit)
        # If life is extinct, start over.
        if len(critters) == 0: break
        if visuals:
            visuals.clear_tree()
            for c in critters: visuals.add_to_tree(c)
        for j, c in enumerate(critters):
            # Set growth rate according to current population
            filenum = len(glob.glob(globcrit))
            evologit([len(critters) - j, "files remaining in iteration", i])
            evologit(c)
            total_time = 0
            growth_rate = get_growth_rate(filenum)
            for g in range(growth_rate):
                if total_time >= max_time: break
                # Make a character for a new name
                n = asciis[g]
                crit = critter.Critter(c, n)
                begin = time.time()
                crit.start()
                while crit.isAlive() and time.time()-begin < time_out and \
                    not should_break():
                    time.sleep(.1)
                crit.join()
                t = time.time() - begin
                total_time += t
                evologit(['    Cycle', g, '/', growth_rate, ':', int(t),
                    'sec, Total:', int(total_time), '/', max_time, 'sec'])
                if visuals: visuals.add_to_tree(n+c)
                # Make sure child exists
                if not is_valid(n+c):
                    total_time = max_time
                    try: os.remove(n + c)
                    except(OSError): pass
                    if visuals: visuals.delete_from_tree(n+c)
                    evologit('        Stillborn')
                else:
                    if not are_different(n+c, c):
                        total_time = max_time
                        os.remove(n + c)
                        if visuals: visuals.delete_from_tree(n+c)
                        evologit(['        ', n + c, 'is a clone'])
                    elif visuals: visuals.graph_file(n+c)
                if should_break(): break
            try: os.remove(c)
            except(OSError): pass
            if visuals: visuals.delete_from_tree(c)
            if should_break(): break
        evologit(['Finished iteration', i])
        if should_break(): break
    if should_quit():
        exit(i)
        break
    else:
        if os.path.exists(state): os.remove(state)
        upload()
        if visuals: visuals.upload = 0
evologit('Exiting')
