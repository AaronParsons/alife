import unittest
from aivolv import comm

class TestComm(unittest.TestCase):
    def test_local(self):
        rx = comm.VolvRX('localhost')
        buf = []
        def packet_handler(data, addr): buf.append(data)
        rx.packet_handler = packet_handler
        rx.start()
        tx = comm.VolvTX('localhost')
        tx.write('test')
        rx.quit()
        self.assertEqual(buf[0], 'test')

if __name__ == '__main__':
    unittest.main()
