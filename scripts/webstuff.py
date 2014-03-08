import urllib, threading, os, zipfile

URL = "http://setiathome.ssl.berkeley.edu/~aparsons/pyvolve/pyvolve_handler.py.cgi"

class Loader(threading.Thread):
    def __init__(self, sleep_period=.1):
        self._stopevent = threading.Event()
        self._sleep_period = sleep_period
        self.t = threading.Thread(target=self.action)
        self.t.setDaemon(1)
        threading.Thread.__init__(self)
    def run(self):
        self.t.start()
        while not self._stopevent.isSet() and self.t.isAlive():
            self._stopevent.wait(self._sleep_period)
        self.end_action()
    def action(self):
        """This function must be overloaded to do something useful."""
        pass
    def end_action(self):
        """This function must be overloaded to do useful cleanup."""
        pass
    def halt(self): self._stopevent.set()
    
class Downloader(Loader):
    def __init__(self, filename, sleep_period=.1):
        self.filename = filename
        Loader.__init__(self, sleep_period=sleep_period)
    def action(self):
        params = urllib.urlencode({'download':1})
        f = urllib.urlopen(URL, params); data = f.read(); f.close()
        f = open(self.filename, 'w'); f.write(data); f.close()
    def end_action(self):
        if not self._stopevent.isSet():
            curdir = os.getcwd()
            newdir = os.path.dirname(self.filename)
            if newdir == '': newdir = '.'
            os.chdir(newdir)
            os.system('unzip %s' % (os.path.basename(self.filename)))
            os.chdir(curdir)
        try: os.remove(self.filename)
        except(OSError): pass

class Uploader(Loader):
    def __init__(self, filename, files, sleep_period=.1):
        self.filename = filename
        self.files = files
        Loader.__init__(self, sleep_period=sleep_period)
    def action(self):
        if len(self.files) == 0: return
        z = zipfile.ZipFile(self.filename, 'w')
        for f in self.files: z.write(f)
        z.close()
        f = open(self.filename, 'rb'); data = f.read(); f.close()
        params = urllib.urlencode({'upload':data})
        f = urllib.urlopen(URL, params); print f.read(); f.close()
    def end_action(self):
        if not self._stopevent.isSet():
            for f in self.files: os.remove(f)
        try: os.remove(self.filename)
        except(OSError): pass

