import unittest, ast, copy, StringIO
import aivolv as ai
from aivolv import mutate

prog = '''
a = 1
b = 2
print a + b
'''

class TestMutate(unittest.TestCase):
    def setUp(self):
        self.dna = {}
        a = ast.parse(prog)
        ai.dna.ast2dna(a,self.dna)
        #print self.dna
    def test_random_pair(self):
        p1 = mutate.random_pair(self.dna)
        self.assertTrue(type(p1) is tuple)
        self.assertTrue(self.dna.has_key(p1[0]))
        self.assertGreater(len(self.dna[p1[0]]), p1[1])
        p2 = mutate.random_pair(self.dna, k='Module')
        self.assertEqual(p2[0], 'Module')
    def test_subkeys(self):
        ks = mutate.subkeys(self.dna, 'Add', 0)
        self.assertEqual(len(ks), 1)
        self.assertEqual(ks[0], ('Add',0))
        ks = mutate.subkeys(self.dna, 'op', 0)
        self.assertEqual(len(ks), 2)
        self.assertEqual(ks[0], ('op',0))
        self.assertEqual(ks[1], ('Add',0))
    def test_swap(self):
        d = copy.deepcopy(self.dna)
        mutate.swap(d, ('int',0),('int',1), 'Module',0)
        self.assertEqual(d['n'][:2], [('int',0),('int',1)])
        self.assertEqual(d['n'][2:], [('int',1),('int',1)])
        self.assertEqual(len(d['Module']), 2)
        d = copy.deepcopy(self.dna)
        d['Print'][0] = mutate.swap(d, ('str',0),('str',1), 'Print',0)
        a = ai.dna.dna2ast(d)
        f = StringIO.StringIO()
        ai.unparse.Unparser(a, f)
        txt = f.getvalue(); f.close()
        lines = txt.splitlines()
        self.assertNotEqual(lines[-1].find('b + b'), -1)
        self.assertNotEqual(lines[-3].find('a = 1'), -1)
    def test_babble(self):
        d = copy.deepcopy(self.dna)
        d['body'][0] = mutate.babble(d, 'body')
        print d['body'][0]
        a = ai.dna.dna2ast(d)
        f = StringIO.StringIO()
        ai.unparse.Unparser(a, f)
        txt = f.getvalue(); f.close()
        print txt

if __name__ == '__main__':
    unittest.main()
