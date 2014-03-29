'''A package for evolving self-replicating scripts.'''
from distutils.core import setup
import os, glob

__version__ = '0.1.0'

setup(name = 'alife',
    version = __version__,
    description = __doc__,
    long_description = __doc__,
    license = 'GPL',
    author = 'Aaron Parsons',
    author_email = 'aparsons@berkeley.edu',
    package_dir = {'alife':'src'},
    packages = ['alife'],
    scripts = glob.glob('scripts/*'),
)
