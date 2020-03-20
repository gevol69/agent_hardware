from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [
    Extension("business_logic", ["business_logic.py"]),
    Extension("main_module", ["main_module.py"]),
    Extension("means", ["means.py"]),
    Extension("gen_ssl", ["gen_ssl.py"])
    ]

setup(
    name = 'Agent',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)