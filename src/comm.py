import socket, select, time, random
import threading
import dna, unparse

PORT = 8088
MAX_PACKETLEN = 8192
MAX_PACKETNUM = 200

class UdpTx:
    def __init__(self, ip, port=PORT):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._dest = (ip, port)
    def send(self, data):
        self._sock.sendto(data, self._dest)

class DnaTx(UdpTx):
    def send_dna(self, d):
        data = dna.serialize(d)
        assert(len(data) <= MAX_PACKETLEN)
        self.send(data)

class UdpRx:
    def __init__(self, host, port=PORT):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setblocking(0)
        self._host = (host,port)
        self._run = False
    def _listen(self):
        self._sock.bind(self._host)
        self._run = True
        while self._run:
            ready = select.select([self._sock], [], [], .1)
            if ready[0]:
                data, addr = self._sock.recvfrom(MAX_PACKETLEN)
                self.packet_handler(data, addr)
    def packet_handler(self, data, addr):
        print addr, len(data)
    def start(self):
        self._rx_thread = threading.Thread(target=self._listen)
        self._rx_thread.start()
    def stop(self):
        self._run = False
        self._rx_thread.join()

class DnaRx(UdpRx):
    lock = threading.Lock()
    data_buf = []
    def packet_handler(self, data, addr):
        self.lock.acquire()
        self.data_buf.insert(0, data)
        self.data_buf = self.data_buf[:MAX_PACKETNUM]
        self.lock.release()
    def iter_dna(self):
        while self._run or len(self.data_buf) > 0:
            if len(self.data_buf) == 0:
                time.sleep(.01)
                continue
            self.lock.acquire()
            pkt = self.data_buf.pop(random.randrange(len(self.data_buf)))
            self.lock.release()
            yield dna.deserialize(pkt)
        return

