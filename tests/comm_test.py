import unittest
from alife import comm

class TestComm(unittest.TestCase):
    def test_local(self):
        rx = comm.UdpRx('localhost')
        buf = []
        def packet_handler(data, addr): buf.append(data)
        rx.packet_handler = packet_handler
        rx.start()
        tx = comm.UdpTx('localhost')
        tx.send('test')
        rx.stop()
        self.assertEqual(buf[0], 'test')
    def test_dna(self):
        dna = {1:2,3:4}
        rx = comm.DnaRx('localhost')
        rx.start()
        tx = comm.DnaTx('localhost')
        tx.send_dna(dna)
        rx.stop()
        for d in rx.iter_dna():
            self.assertEqual(dna, d)
    #def test_memory(self):
    #    rx = comm.DnaRx('localhost')
    #    rx.start()
    #    tx = comm.DnaTx('localhost')
    #    dna = {1:2,3:4}
    #    while True:
    #        tx.send_dna(dna)

if __name__ == '__main__':
    unittest.main()
