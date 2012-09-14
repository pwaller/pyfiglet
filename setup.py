#!/usr/bin/env python

from setuptools import setup

setup(name='pyfiglet',
      version='0.6.1',
      description='Pure-python FIGlet implementation',
      author='Peter Waller (Thanks to Christopher Jones and Stefano Rivera)',
      author_email='peter.waller@gmail.com',
      url='https://github.com/pwaller/pyfiglet',
      packages=['pyfiglet', 'pyfiglet.fonts'],
      package_data={'pyfiglet.fonts' : ['*.flf']},
)

