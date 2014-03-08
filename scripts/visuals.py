'''This module provides a visualization interface for pyvolve.'''

import blt_graph, Pmw, os, Tkinter
from numarray import *
from numarray.convolve import correlate

def get_array(filename):
    '''Return an integer array, centered around zero, representing the
    ascii content of a file.'''
    f = open(filename); data = f.read(); f.close()
    a = array(data.replace(' ',''))
    return a - average(a)

def name2arr(name):
    '''Return a float array representing the geneological history of
    a critter, deduced from it's name.'''
    L = list(name[:-3]); L.reverse()
    a = array(''.join(L)).astype(Float) - 97
    n = len(a)
    a *= (arange(n, type=Float) - n/2.) / (n/2.)
    return cumsum(a)

class PyvolveGraph:
    def __init__(self, parent, eve='3.py', max_graphs=5, graph_size=1000):
        self.menu_bar = Pmw.MenuBar(parent)
        self.menu_bar.pack(fill='x')
        self.menu_bar.addmenu('File', None, tearoff=True)
        self.menu_bar.addmenuitem('File', 'command', \
            label='Upload', command=self.do_upload)
        self.menu_bar.addmenuitem('File', 'command', \
            label='Quit', command=self.quit)
        f1 = Tkinter.Frame(parent)
        f1.pack(side='top', expand=True, fill='both')
        f2 = Tkinter.Frame(parent)
        f2.pack(side='bottom', expand=True, fill='both')
        self.g = blt_graph.ZoomGraph(f1)
        self.g.axes_off()
        self.tree = blt_graph.ZoomGraph(f2)
        self.label_list = {}
        self.tree.axes_off()
        self.tree.legend_off()
        self.text = Pmw.ScrolledText(f1,
            vscrollmode='dynamic', hscrollmode='dynamic', labelpos='n',
            label_text='Event Log', text_width=40, text_height=8,
            text_wrap='none')
        self.text.pack(side='bottom', expand=True, fill='x')
        self.eve = get_array(eve)
        self.graph_list = []
        self.MAX_GRAPHS = max_graphs
        self.GRAPH_SIZE = graph_size
        self.go = 1
        self.upload = 0
    def quit(self): self.go = 0
    def do_upload(self): self.upload = 1
    def graph_file(self, filename):
        self.graph_list += [os.path.basename(filename)]
        if len(self.graph_list) > self.MAX_GRAPHS:
            self.g.delete(self.graph_list[0])
            del(self.graph_list[0])
        self.g.graph(y=self.normalize(correlate(self.eve, \
            get_array(filename))), label=self.graph_list[-1])
    def normalize(self, a):
        s = a.shape; every = len(a) / self.GRAPH_SIZE
        a = resize(a, s[:-1] + (s[-1] / every, every))[...,0]
        return a / a.max()
    def add_text(self, txt):
        self.text.appendtext(txt)
    def delete_from_tree(self, name):
        if name in self.label_list.keys():
            self.tree.delete(name)
            del(self.label_list[name])
    def add_to_tree(self, name):
        A = name2arr(name); L = str(abs(A[-1]))
        self.tree.graph(A, label=L, smooth='natural')
        self.label_list[L] = 0
    def clear_tree(self):
        label_list = self.label_list.keys()
        for L in label_list: self.delete_from_tree(L)
    def show(self):
        self.g.show()
