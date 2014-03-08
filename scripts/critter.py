import threading, sys, os, subprocess

class Critter(threading.Thread):
    def __init__(self, filename, child_char, sleep_period=.1):
        self.myenv = {}
        self._stopevent = threading.Event()
        self._sleep_period = sleep_period
        threading.Thread.__init__(self, name=filename)
        self.filename = filename
        dir, name = os.path.dirname(filename), os.path.basename(filename)
        if dir == '': dir = '.'
        self.child = open(dir + os.sep + child_char + name, 'w')
    def run(self):
        try: os.chmod(self.filename, 0777)
        except(OSError): return
        process = subprocess.Popen([self.filename], 
            stdout=self.child, stderr=open('/dev/null', 'w'))
        while not self._stopevent.isSet() and process.poll() == None:
            self._stopevent.wait(self._sleep_period)
        if process.poll() == None: os.kill(process.pid, 9)
    def join(self, timeout=None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)
