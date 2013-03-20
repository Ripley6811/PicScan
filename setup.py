#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
(SUMMARY)

To create a release, enter the following in cmd:
python setup.py sdist

:REQUIRES: ...
:PRECONDITION: ...
:POSTCONDITION: ...

:AUTHOR: Ripley6811
:ORGANIZATION: National Cheng Kung University, Department of Earth Sciences
:CONTACT: python@boun.cr
:SINCE: Thu Feb 28 00:12:19 2013
:VERSION: 0.1
:STATUS: Nascent
:TODO: ...
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Thu Feb 28 00:12:19 2013'
__version__ = '0.1'

#===============================================================================
# SETUP
#===============================================================================

from distutils.core import setup

setup(
    name='PicScan',
    version='0.1.0',
    author='Ripley6811',
    author_email='python@boun.cr',
    packages=['picscan',],
    license='LICENSE.txt',
    long_description=open('README.txt').read(),
    install_requires=[
        "NumPy >= 1.1.1",
    ],
)