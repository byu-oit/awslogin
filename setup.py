#!/usr/bin/env python3

import os
import sys
import subprocess
from setuptools import setup, find_packages

if int(sys.version[0]) < 3:
    sys.stderr.write("byu_awslogin requires python 3\n")
    sys.exit(-1)

subprocess.check_call('pandoc --from=markdown --to=rst --output=README.rst README.md', shell=True)
with open("README.rst") as rm_file:
    long_description = rm_file.read()
os.remove('README.rst')

def get_requirements():
    with open('requirements.txt') as obj:
        lines = [dep for dep in obj.read().split('\n') if dep]
        return lines

setup(name='byu_awslogin',
      version='0.9.6',
      description="An aws-adfs spinoff that fits BYU's needs",
      long_description=long_description,
      author='BYU OIT Application Development',
      author_email='it@byu.edu',
      url='https://github.com/byu-oit/awslogin',
      packages=find_packages(),
      data_files=[('', ['README.md', 'LICENSE'])],
      license="Apache 2",
      install_requires=get_requirements(),
      zip_safe=True,
      entry_points={
          'console_scripts': ['awslogin=byu_awslogin.index:cli']
      }
      )
