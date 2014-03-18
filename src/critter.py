import dna
import hashlib, ctypes, threading

tempfile = 'eden/%s.py'

def hashtxt(txt):
    return hashlib.sha224(txt).hexdigest()[:10]

class Critter:
    def __init__(self, d, tempfile=tempfile):
        self.txt = dna.dna2txt(d)
        self.my_id = hashtxt(self.txt)
        self.filename = tempfile % self.my_id
    def _run(self):
        #sys.stdout = open(os.devnull, 'w')
        #sys.stderr = open(os.devnull, 'w')
        try:
            f = open(self.filename, 'w'); f.write(self.txt); f.close()
            env = {
                '__file__':self.filename,
                '__name__':'__main__',
            }
            execfile(self.filename, env)
        except: pass
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
