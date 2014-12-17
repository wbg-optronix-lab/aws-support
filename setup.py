#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='aws-simulations',
    version='0.9.0',
    url='',
    author='Neil Newman, Jonathan Marini',
    author_email='nnewman2@albany.edu, jmarini@ieee.org',
    packages=['aws_simulations'],
    install_requires=['boto'],
    test_suite='tests',
)
