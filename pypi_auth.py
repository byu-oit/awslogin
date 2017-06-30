#!/usr/bin/env python

import boto3
import configparser
from os.path import expanduser

def load_config(prefix, var_names):
    ssm = boto3.client('ssm')
    config = {}
    response = ssm.get_parameters(Names=[prefix + '.' + name for name in var_names], WithDecryption=True)
    if not response['Parameters']:
        raise Exception('Could not find the parameters requested.')
    for parameter in response['Parameters']:
        config[parameter['Name'].replace(prefix+'.','')] = parameter['Value']
    return config

# update the patch version automatically if we every want to
#with open('VERSION') as verobj:
#    major, minor, patch = verobj.read().split('.')
#newpatch = str(int(patch) + 1)
#newversion = '.'.join([major, minor, newpatch])
#with open('VERSION', 'w') as verobj:
#    verobj.write(newversion)

# write the ~/.pypirc file
params = load_config('byu-awslogin.prd', ['pypi_username', 'pypi_password'])
config = configparser.ConfigParser()
config['distutils'] = {'index-servers': 'pypi'}
config['pypi'] = {'username': params['pypi_username'], 'password': params['pypi_password']}
with open('{}/.pypirc'.format(expanduser('~')), 'w') as pypirc:
    config.write(pypirc)
