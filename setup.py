'''A package for evolving self-replicating scripts.'''
from distutils.core import setup
import os, glob

__version__ = '0.0.1'

setup(name = 'aivolv',
    version = __version__,
    description = __doc__,
    long_description = __doc__,
    license = 'GPL',
    author = 'Aaron Parsons',
    author_email = 'aparsons@berkeley.edu',
    package_dir = {'aivolv':'src'},
    packages = ['aivolv'],
    scripts = glob.glob('scripts/*'),
)
