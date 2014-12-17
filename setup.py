#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='aws-support',
    version='0.10.0',
    url='',
    author='Neil Newman, Jonathan Marini',
    author_email='nnewman2@albany.edu, jmarini@ieee.org',
    packages=['aws_support'],
    install_requires=['boto', 'paramiko'],
    test_suite='tests',
)
