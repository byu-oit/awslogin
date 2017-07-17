#!/usr/bin/env python3

import os
import sys
import subprocess
from setuptools import setup, find_packages

if not sys.version.startswith('3.6'):
    sys.stderr.write("byu_awslogin requires python 3.6\n")
    sys.exit(-1)

with open("README.rst") as rm_file:
    long_description = rm_file.read()

def get_requirements():
    with open('requirements.txt') as obj:
        lines = [dep for dep in obj.read().split('\n') if dep]
        return lines

VERSION = ''
with open('VERSION') as verobj:
    VERSION = verobj.read()

setup(name='byu_awslogin',
      version=VERSION,
      description="An aws-adfs spinoff that fits BYU's needs",
      long_description=long_description,
      author='BYU OIT Application Development',
      author_email='it@byu.edu',
      url='https://github.com/byu-oit/awslogin',
      packages=find_packages(),
      license="Apache 2",
      install_requires=get_requirements(),
      zip_safe=True,
      entry_points={
          'console_scripts': ['awslogin=byu_awslogin.index:main']
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Education',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3 :: Only',
          'Natural Language :: English',
          'Topic :: Utilities'
      ]
)
