#!/usr/bin/env python

from setuptools import setup

setup(
name='aleparser',
    version='0.1',
    description='A simple python ALE (AvidLogExchange) parser.',
    author='Jacob Smith',
    author_email='kloptops@gmail.com',
    license = 'Public Domain',
    url='https://github.com/kloptops',
    packages=['aleparser'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        ],
    test_suite = 'tests',
    )
