#!/usr/bin/env python

from setuptools import setup
import sys
from os import path
import shutil

# Set up minimum fonts if none already present
here = path.abspath(path.dirname(__file__))
pkg_src = path.join(here, 'pyfiglet', 'fonts')
repo_src = path.join(here, 'pyfiglet', 'fonts-standard')
if not path.isdir(pkg_src):
    shutil.copytree(repo_src, pkg_src)

def get_version():
    sys.path.insert(0, 'pyfiglet')
    from version import __version__
    sys.path.pop(0)
    return __version__

setup(
    name='pyfiglet',
    version=get_version(),
    description='Pure-python FIGlet implementation',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        # For Katakana
        'Natural Language :: Japanese',
        # For Cyrillic
        'Natural Language :: Bulgarian',
        'Natural Language :: Bosnian',
        'Natural Language :: Macedonian',
        'Natural Language :: Russian',
        'Natural Language :: Serbian',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Fonts',
    ],
    author='Peter Waller (Thanks to Christopher Jones and Stefano Rivera)',
    author_email='p@pwaller.net',
    url='https://github.com/pwaller/pyfiglet',
    packages=['pyfiglet', 'pyfiglet.fonts'],
    package_data={'pyfiglet.fonts': ['*.flf', '*.flc']},
    entry_points={
        'console_scripts': [
            'pyfiglet = pyfiglet:main',
        ],
    }
)
