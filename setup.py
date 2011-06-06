from distutils.core import setup
from distutils.extension import Extension
import Cython
from Cython.Distutils import build_ext
import numpy as np

ext_modules = [Extension("ell1", ["ell1.pyx"], include_dirs=[np.get_include()])]

setup(
  name = 'L1 optimization',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
