from . import dna
import hashlib, ctypes

# Using threading (as opposed to processes) for critters seems to be faster, and doesn't
# suffer from opening too many files (Processes direct stdin/out to /dev/null and have to open it).
# However, threads are hard to terminate, and the code for getting around that is very hacky.
THREADING = True
if THREADING: import threading
else: import multiprocessing as mp

TEMPFILE = 'eden/%s.py'

def hashtxt(txt):
    return hashlib.sha224(txt.encode('utf-8')).hexdigest()[:10]

class Critter:
    def __init__(self, d, tempfile=TEMPFILE):
        self.txt = dna.dna2txt(d)
        self.my_id = hashtxt(self.txt)
        self.filename = tempfile % self.my_id
        self._interrupt = False
        self.thread = None
    def _run(self):
        try:
            env = {
                '__file__':self.filename,
                '__name__':'__main__',
            }
            with open(self.filename, 'rb') as f:
                exec(compile(f.read(), self.filename, 'exec'), env)
        except(RuntimeError): pass # this is a normal exit mode for interruption
        except: pass
    def run(self):
        self._interrupt = False
        f = open(self.filename, 'w'); f.write(self.txt); f.close()
        if THREADING: self.thread = threading.Thread(target=self._run, name=self.my_id)
        else: self.thread = mp.Process(target=self._run, name=self.my_id)
        self.thread.daemon = True
        self.thread.start()
    def join(self):
        self.thread.join()
    def is_alive(self):
        # the _interrupt flag is used as proxy when a thread is doomed but still alive, speeding its removal
        return (not self._interrupt) and self.thread.is_alive()
        #return self.thread.is_alive()
    def interrupt(self):
        if not self.is_alive(): return
        self._interrupt = True
        if THREADING:
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(self.thread.ident),
                    ctypes.py_object(RuntimeError))
            if res > 1:
                # "if it returns a number greater than one, you're in trouble,
                # and you should call it again with exc=NULL to revert the effect"
                ctypes.pythonapi.PyThreadState_SetAsyncExc(self.thread.ident, 0)
                raise SystemError("PyThreadState_SetAsyncExc failed")
        else:
            self.thread.terminate()
    #def __del__(self):
    #    self.interrupt()
    #    self.join()
