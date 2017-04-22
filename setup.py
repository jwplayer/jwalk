# -*- coding: utf-8 -*-
"""Distutils setup file, used to install or test 'jwalk'."""
from __future__ import print_function

import sys
import textwrap
import pkg_resources
from setuptools import setup, find_packages, Extension

with open('README.rst') as f:
    readme = f.read()


def is_installed(requirement):
    try:
        pkg_resources.require(requirement)
    except pkg_resources.ResolutionError:
        return False
    else:
        return True


if not is_installed('numpy'):
    print(textwrap.dedent("""
            Error: numpy needs to be installed first. You can install it via:

            $ pip install numpy
            """), file=sys.stderr)
    exit(1)


def ext_modules():
    import numpy

    walks_ext = Extension('jwalk.walks', ['jwalk/src/walks.pyx'],
                          include_dirs=[numpy.get_include()])

    return [walks_ext]


setup(
    name='jwalk',
    description='Representational learning on graphs',
    long_description=readme,
    packages=find_packages(exclude=['tests', 'docs']),
    use_scm_version=True,
    ext_modules=ext_modules(),
    author='Kamil Sindi, Nir Yungster',
    author_email='kamil@jwplayer.com, nir@jwplayer.com',
    url='https://github.com/jwplayer/jwalk',
    install_requires=[
        'setuptools_scm>=1.15.0',
        'Cython',
        'numpy',
        'scipy',
        'gensim>=2.0.0',
        'joblib',
    ],
    setup_requires=[
        'setuptools>=18.0',
        'Cython>=0.20',
        'numpy',
        'pytest-runner',
        'setuptools_scm>=1.15.0',
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
