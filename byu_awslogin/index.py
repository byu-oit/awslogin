#!/usr/bin/env python3

import os
import fire
import getpass
import subprocess
import configparser
from os.path import expanduser
from .adfs_auth import authenticate
from .assume_role import ask_which_role_to_assume, assume_role
from .roles import action_url_on_validation_success, retrieve_roles_page

def cli(account=None, role=None):
    # Get the federated credentials from the user
    cached_netid = load_last_netid()
    if cached_netid:
        net_id_prompt = 'BYU Net ID [{}]: '.format(cached_netid)
    else:
        net_id_prompt = 'BYU Net ID: '
    net_id = input(net_id_prompt) or cached_netid
    if "@byu.local" in net_id:
        print('@byu.local is not required')
        username = net_id
    else:
        username = '{}@byu.local'.format(net_id)
    password = getpass.getpass()
    print('')

    ####
    # Authenticate against ADFS with DUO MFA
    ####
    html_response, session, auth_signature, duo_request_signature = authenticate(username, password)

    ####
    # Obtain the roles available to assume
    ####
    roles_page_url = action_url_on_validation_success(html_response)
    account_names, principal_roles, assertion, aws_session_duration = retrieve_roles_page(
        roles_page_url,
        html_response,
        session,
        auth_signature,
        duo_request_signature,
    )

    ####
    # Ask user which role to assume
    ####
    #print(principal_roles)
    account_name, role_name, chosen_role = ask_which_role_to_assume(account_names, principal_roles, account, role)

    ####
    # Assume role and set in the environment
    ####
    aws_session_token = assume_role(*chosen_role, assertion)

    write_to_cred_file(aws_session_token)
    write_to_config_file(net_id, 'us-west-2')

    print("Now logged into {}@{}".format(role_name, account_name))
    #proc = subprocess.Popen(args, env=os.environ)

    # Overwrite and delete the credential variables, just for safety
    username = '##############################################'
    password = '##############################################'
    del username
    del password

def main():
    fire.Fire(cli)


def open_config_file(file):
    config = configparser.ConfigParser()
    config.read(file)
    return config


def write_to_cred_file(aws_session_token):
    check_for_aws_dir()
    file = "{}/.aws/credentials".format(expanduser('~'))
    config = open_config_file(file)
    config['default'] = {'aws_access_key_id': aws_session_token['Credentials']['AccessKeyId'],
                         'aws_secret_access_key': aws_session_token['Credentials']['SecretAccessKey'],
                         'aws_session_token': aws_session_token['Credentials']['SessionToken']
                        }
    with open(file, 'w') as configfile:
        config.write(configfile)


def check_for_aws_dir():
    directory = "{}/.aws".format(expanduser('~'))
    if not os.path.exists(directory):
        os.makedirs(directory)
    file = "{}/config".format(directory)


def write_to_config_file(net_id, region):
    check_for_aws_dir()
    file = "{}/.aws/config".format(expanduser('~'))
    config = open_config_file(file)
    config['default'] = {'region': region, 'adfs_netid': net_id}
    with open(file, 'w') as configfile:
        config.write(configfile)


def load_last_netid():
    file = "{}/.aws/config".format(expanduser('~'))
    config = open_config_file(file)
    if config.has_section('default') and config.has_option('default', 'adfs_netid'):
        return config['default']['adfs_netid']
    else:
        return ''


if __name__ == '__main__':
    main()