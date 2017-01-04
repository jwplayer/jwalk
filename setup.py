# -*- coding: utf-8 -*-
"""Distutils setup file, used to install or test 'jwalk'."""
import textwrap

import numpy as np
from setuptools import setup, find_packages, Extension

try:
    from Cython.Distutils import build_ext  # noqa: F401
except ImportError:
    USE_CYTHON = False
else:
    USE_CYTHON = True

ext = '.pyx' if USE_CYTHON else '.c'
ext_modules = [Extension('jwalk.walks', ['jwalk/src/walks' + ext],
                         include_dirs=[np.get_include()])]

if USE_CYTHON:
    from Cython.Build import cythonize

    ext_modules = cythonize(ext_modules)

with open('README.rst') as f:
    readme = f.read()

setup(
    name='jwalk',
    description='Representational learning on graphs',
    long_description=readme,
    packages=find_packages(exclude=['tests', 'docs']),
    use_scm_version=True,
    ext_modules=cythonize(ext_modules),
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
