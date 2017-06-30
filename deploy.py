#!/usr/bin/env python

import subprocess

def call(cmd):
    print('Running \'{}\'...'.format(cmd))
    subprocess.check_call(cmd, shell=True)

print('Remember to update the version in setup.py.  I will open open that up for you now just in case you forgot.')
input('Press enter to proceed ')
call('vim setup.py')
call('rm -fr dist')
call('pip install -r requirements.txt')
call('python setup.py sdist bdist_wheel')
call('twine upload dist/*')
