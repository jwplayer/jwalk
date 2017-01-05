# -*- coding: utf-8 -*-
"""Distutils setup file, used to install or test 'jwalk'."""
import textwrap

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext as _build_ext

extensions = [Extension('jwalk.walks', ['jwalk/src/walks.pyx'])]

with open('README.rst') as f:
    readme = f.read()


class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        try:
            __builtins__.__NUMPY_SETUP__ = False
        except AttributeError:
            pass
        import numpy as np
        self.include_dirs.append(np.get_include())


setup(
    name='jwalk',
    description='Representational learning on graphs',
    long_description=readme,
    packages=find_packages(exclude=['tests', 'docs']),
    cmdclass={'build_ext': build_ext},
    use_scm_version=True,
    ext_modules=extensions,
    author='Kamil Sindi, Nir Yungster',
    author_email='kamil@jwplayer.com, nir@jwplayer.com',
    url='https://github.com/jwplayer/jwalk',
    install_requires=[
        'setuptools_scm',
        'Cython',
        'numpy',
        'scipy',
        'gensim>=0.13.4',
        'joblib',
    ],
    setup_requires=[
        'setuptools>=18.0',
        'Cython>=0.20',
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
