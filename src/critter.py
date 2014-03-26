import dna
import hashlib, ctypes

THREADING = True
if THREADING: import threading
else: from multiprocessing import Process

TEMPFILE = 'eden/%s.py'

def hashtxt(txt):
    return hashlib.sha224(txt).hexdigest()[:10]

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
            execfile(self.filename, env)
        #except(RuntimeError): pass # this is a normal exit mode for interruption
        except: pass # this is a normal exit mode for interruption
    def run(self):
        self._interrupt = False
        f = open(self.filename, 'w'); f.write(self.txt); f.close()
        if THREADING: self.thread = threading.Thread(target=self._run, name=self.my_id)
        else: self.thread = Process(target=self._run)
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
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(self.thread.ident),
                ctypes.py_object(RuntimeError))
        if res > 1:
            # "if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self.thread.ident, 0)
            raise SystemError("PyThreadState_SetAsyncExc failed")
    #def __del__(self):
    #    self.interrupt()
    #    self.join()
