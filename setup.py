#!/usr/bin/env python

from setuptools import setup

setup(name='pyfiglet',
      version='0.4',
      description='Pure-python FIGlet implementation',
      author='Christopher Jones',
      author_email='cjones@insub.org',
      url='http://sourceforge.net/projects/pyfiglet/',
      packages=['pyfiglet', 'pyfiglet.fonts'],
      package_data={'pyfiglet.fonts' : ['pyfiglet/fonts/*.flf']},
)

