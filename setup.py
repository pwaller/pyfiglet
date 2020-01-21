#!/usr/bin/env python

from setuptools import setup, find_packages
import os, sys


def get_version():
    sys.path.insert(0, 'pyfiglet')
    from version import __version__
    sys.path.pop(0)
    return __version__


def read_readme(): # For reading the README.md
    with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
        return f.read().rstrip()

def parse_requirements(): # Used if requirements are set
    with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as f:
        return f.read().strip().splitlines()

def add_fonts():
    # To make sure some fonts don't get loaded, due to their encryption
    included = ["*.flf", "*.flc"]
    excluded = ["ascii9", "ascii12", "smascii", "mono", "bigmono", "smascii", "bigascii", "smmono"]
    _excl = tuple(excluded)
    for font in os.listdir(os.path.join(os.path.dirname(__file__), "pyfiglet", "fonts")):
        if os.path.splitext(font)[1] == ".tlf":
            if not font.startswith(_excl):
                included.append(font)

    return included

setup(
    name='pyfiglet',
    version=get_version(),
    description='Pure-python FIGlet implementation',
    long_description=read_readme(),
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Fonts',
    ],
    author='Peter Waller (Thanks to Christopher Jones and Stefano Rivera)',
    author_email='p@pwaller.net',
    url='https://github.com/pwaller/pyfiglet',
    packages=find_packages(),
    package_data={'pyfiglet.fonts': add_fonts()},
    entry_points={
        'console_scripts': [
            'pyfiglet = pyfiglet:main',
        ],
    }
)
