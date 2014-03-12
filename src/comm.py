import socket, cPickle, StringIO, hashlib, threading
import dna, unparse

PORT = 8088

class VolvTX:
    def __init__(self, ip, port=PORT):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._dest = (ip, port)
    def write(self, data):
        self._sock.sendto(data, self._dest)

class VolvRX:
    def __init__(self, host, port=PORT, maxbuf=4096):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._host = (host,port)
        self.maxbuf = maxbuf
        self._run = False
    def _listen(self):
        self._sock.bind(self._host)
        self._run = True
        while self._run:
            data, addr = self._sock.recvfrom(self.maxbuf)
            self.packet_handler(data, addr)
    def packet_handler(self, data, addr):
        print addr
        dna = cPickle.loads(data)
        ast = dna.dna2ast(dna)
        f = StringIO.StringIO()
        unparse.Unparser(ast,f)
        txt = f.getvalue(); f.close()
        hsh = hashlib.sha224(txt).hexdigest()
        print hsh
        print '-'*10
    def start(self):
        self._rx_thread = threading.Thread(target=self._listen)
        self._rx_thread.start()
    def quit(self):
        self._run = False
        self._rx_thread.join()
