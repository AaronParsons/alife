import unittest
import ast
import astunparse
import alife as ai

prog = '''
a = 1
b = 2
print((a + b))
'''

class TestDNA(unittest.TestCase):
    def test_ast(self):
        a = ast.parse(prog)
        prog2 = astunparse.unparse(a)
        self.assertEqual(prog, prog2)
    def test_simple_parse(self):
        dna = ai.dna.DNA(txt=prog)
        prog2 = dna.to_txt()
        self.assertEqual(prog, prog2)
    def test_simple_mutate(self):
        dna = ai.dna.DNA(txt=prog)
        body = dna['body'][0]
        dna['body'] = [[body[1], body[0], body[2]]]
        prog2 = dna.to_txt()
        lines = prog.splitlines()
        lines = [lines[0], lines[2], lines[1], lines[3]]
        prog3 = '\n'.join(lines) + '\n'
        self.assertEqual(prog2, prog3)

if __name__ == '__main__':
    unittest.main()
