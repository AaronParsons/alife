import unittest, os, threading
from alife import critter
from alife import dna

test_prog = \
'''import time
while True: time.sleep(.1)
'''

test_dna = dna.DNA(txt=test_prog)

class TestCritter(unittest.TestCase):
    def setUp(self):
        self.critter = critter.Critter(test_dna)
        self.tempfile = self.critter.filename
    def tearDown(self):
        os.remove(self.tempfile)
    def test_interrupt(self):
        self.critter.run()
        self.assertTrue(self.critter.is_alive())
        self.assertTrue(os.path.exists(self.tempfile))
        self.critter.interrupt()
        self.critter.join()
        self.assertFalse(self.critter.is_alive())
    #def test_deletion(self):
    #    c = critter.Critter(test_dna, tempfile=self.tempfile)
    #    c.run()
    #    i = c.thread.ident
    #    del(c)
    #    #del(c)
    #    #cnt3 = threading.active_count()
    #    #import time; time.sleep(3)
    #    #print cnt1, cnt2, cnt3
    #    #for t in threading.enumerate():
    #    #    if i == t.ident: t.join()
    #    #for t in threading.enumerate():
    #    #    self.assertNotEqual(i, t.ident)
    #    #self.assertEqual(cnt1, cn3)

if __name__ == '__main__':
    unittest.main()
