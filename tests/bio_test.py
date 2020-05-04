import unittest, os, threading, time
import multiprocessing as mp
from alife import bio
from alife import dna

test_prog = \
'''import time
while True: time.sleep(.1)
'''

evil_prog = \
'''raise SyntaxError
'''


class TestBio(unittest.TestCase):
    def setUp(self):
        self.test_dna = dna.DNA(txt=test_prog)
        self.evil_dna = dna.DNA(txt=evil_prog)
        self.q = mp.Queue()
    def tearDown(self):
        self.q.close()
        #os.remove(self.tempfile % self.critter.my_id)
    def test_basics(self):
        b = bio.BioSphere('test', self.q)
        b.run()
        self.assertTrue(b.is_alive())
        b.send_dna(self.test_dna)
        b.stop()
        b.join()
        self.assertFalse(b.is_alive())
    def test_evil(self):
        b = bio.BioSphere('test', self.q)
        b.run()
        self.assertTrue(b.is_alive())
        b.send_dna(self.evil_dna)
        time.sleep(1)
        b.stop()
        b.join()
        self.assertFalse(b.is_alive())
    def test_clean(self):
        b = bio.BioSphere('test', self.q, max_critters=3)
        b.run()
        self.assertTrue(b.is_alive())
        for i in range(50): b.send_dna(self.test_dna)
        time.sleep(1)
        b.stop()
        b.join()
        self.assertFalse(b.is_alive())
        
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
