# -*- coding: utf-8 -*-
"""Distutils setup file, used to install or test 'jwalk'."""
import textwrap

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext as _build_ext

try:
    from Cython.Distutils import build_ext_  # noqa: F401
except ImportError:
    USE_CYTHON = False
else:
    USE_CYTHON = True

ext = '.pyx' if USE_CYTHON else '.c'
ext_modules = [Extension('jwalk.walks', ['jwalk/src/walks' + ext])]

if USE_CYTHON:
    from Cython.Build import cythonize

    ext_modules = cythonize(ext_modules)

with open('README.rst') as f:
    readme = f.read()


class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())


setup(
    name='jwalk',
    description='Representational learning on graphs',
    long_description=readme,
    packages=find_packages(exclude=['tests', 'docs']),
    cmdclass={'build_ext': build_ext},
    use_scm_version=True,
    ext_modules=ext_modules,
    author='Kamil Sindi, Nir Yungster',
    author_email='kamil@jwplayer.com, nir@jwplayer.com',
    url='https://github.com/jwplayer/jwalk',
    install_requires=[
        'cython',
        'numpy',
        'scipy',
        'gensim',
        'joblib',
    ],
    setup_requires=[
        'cython',
        'numpy',
        'pytest-runner',
        'setuptools_scm',
        'sphinx_rtd_theme',
    ],
    tests_require=[
        'pytest',
        'pytest-flake8',
    ],
    extras_require={
        'all': ['pandas'],
        ':python_version=="2.7"': ['mock'],
    },
    zip_safe=False,
    include_package_data=True,
    classifiers=textwrap.dedent("""
        Development Status :: 4 - Beta
        Intended Audience :: Science/Research
        License :: OSI Approved :: Apache Software License
        Environment :: Console
        Programming Language :: Python :: 2
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.4
        Programming Language :: Python :: 3.5
        Programming Language :: Python :: 3.6
        Programming Language :: Cython
        Topic :: Scientific/Engineering
        """).strip().splitlines(),
    keywords=['deep learning', 'neural networks', 'deepwalk'],
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
            'jwalk=jwalk.__main__:main'
        ]
    },
)
