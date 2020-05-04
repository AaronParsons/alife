import hashlib
from ctypes import pythonapi, c_long, py_object

# Using threading (as opposed to processes) for critters seems faster, 
# and doesn't  suffer from opening too many files (Processes direct 
# stdin/out to /dev/null and have to open it).  However, threads are 
# hard to terminate, and the code for getting around that is hacky.

THREADING = True
if THREADING: import threading
else: import multiprocessing as mp

FILE_TEMPLATE = 'eden/%s.py'

def hashtxt(txt):
    '''Create a hash of text for tracking purposes.'''
    return hashlib.sha224(txt.encode('utf-8')).hexdigest()[:10]

class Critter:
    '''An interface for instantiating DNA as a process.'''
    def __init__(self, dna, file_template=FILE_TEMPLATE):
        '''dna: alife.dna.DNA object
        file_template: string of form "dir/%s.py".'''
        self.txt = dna.to_txt()
        self.my_id = hashtxt(self.txt)
        self.filename = file_template % self.my_id
        self._interrupt = False
        self.thread = None

    def _run(self):
        '''Execute critter code in fresh env, catching exceptions.'''
        try:
            env = {
                '__file__': self.filename,
                '__name__': '__main__',
            }
            exec(compile(self.txt, self.filename, 'exec'), env)
        except(RuntimeError):
            # this is a normal exit mode for interruption
            pass
        except:
            # this is protection against mutated DNA
            pass

    def run(self):
        '''Start thread corresponding to this critter.'''
        self._interrupt = False
        with open(self.filename, 'w') as f:
            f.write(self.txt)
        if THREADING:
            self.thread = threading.Thread(target=self._run,
                                           name=self.my_id)
        else:
            self.thread = mp.Process(target=self._run,
                                     name=self.my_id)
        self.thread.daemon = True
        self.thread.start()

    def join(self):
        '''Join with critter thread.'''
        self.thread.join()

    def is_alive(self):
        '''See if critter thread is still active.'''
        # _interrupt flag used as proxy when a thread is doomed 
        # but still alive, speeding removal
        return (not self._interrupt) and self.thread.is_alive()
        #return self.thread.is_alive()

    def interrupt(self):
        '''Try to force critter to stop.'''
        if not self.is_alive():
            return
        self._interrupt = True
        if THREADING:
            res = pythonapi.PyThreadState_SetAsyncExc(
                    c_long(self.thread.ident),
                    py_object(RuntimeError))
            if res > 1:
                # "a number greater than one means you're in trouble,
                # and must call again with exc=NULL to revert the effect"
                pythonapi.PyThreadState_SetAsyncExc(self.thread.ident, 0)
                raise SystemError("PyThreadState_SetAsyncExc failed")
        else:
            self.thread.terminate()

    #def __del__(self):
    #    self.interrupt()
    #    self.join()
