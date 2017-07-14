#!/usr/bin/env python3

import os
import sys
import fire
import getpass
import configparser
from os.path import expanduser
try:
    import lxml.etree as ET
except ImportError:
    import platform
    if platform.system() == 'Windows':
        print('awslogin will not run on your machine yet.  Please follow the instructions at https://github.com/byu-oit/awslogin/releases/tag/lxml to get it running.')
        sys.exit(1)
    else:
        raise
from .adfs_auth import authenticate
from .assume_role import ask_which_role_to_assume, assume_role
from .roles import action_url_on_validation_success, retrieve_roles_page


def cli(account=None, role=None, profile='default'):
    # Get the federated credentials from the user
    cached_netid = load_last_netid(aws_file('config'), profile)
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

    # Overwrite and delete the credential variables, just for safety
    username = '##############################################'
    password = '##############################################'
    del username
    del password

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
    account_roles = ask_which_role_to_assume(account_names, principal_roles, account, role)

    ####
    # Assume roles and set in the environment
    ####
    for account_role in account_roles:
        aws_session_token = assume_role(account_role, assertion)

        # If assuming roles across all accounts, then use the account name as the profile name
        if account == 'all':
            profile = account_role.account_name

        check_for_aws_dir()
        write_to_cred_file(aws_file('creds'), aws_session_token, profile)
        write_to_config_file(aws_file('config'), net_id, 'us-west-2', profile)

        print("Now logged into {}@{}".format(account_role.role_name, account_role.account_name))


def main():
    if not sys.version.startswith('3.6'):
        sys.stderr.write("byu_awslogin requires python 3.6\n")
        sys.exit(-1)
    fire.Fire(cli)


def aws_file(file_type):
    if file_type == 'creds':
        return "{}/.aws/credentials".format(expanduser('~'))
    else:
        return "{}/.aws/config".format(expanduser('~'))


def open_config_file(file):
    config = configparser.ConfigParser()
    config.read(file)
    return config


def check_for_aws_dir(directory="{}/.aws".format(expanduser('~'))):
    if not os.path.exists(directory):
        os.makedirs(directory)


def write_to_cred_file(file, aws_session_token, profile):
    config = open_config_file(file)
    config[profile] = {
        'aws_access_key_id': aws_session_token['Credentials']['AccessKeyId'],
        'aws_secret_access_key': aws_session_token['Credentials']['SecretAccessKey'],
        'aws_session_token': aws_session_token['Credentials']['SessionToken']
    }
    with open(file, 'w') as configfile:
        config.write(configfile)


def write_to_config_file(file, net_id, region, profile):
    config = open_config_file(file)
    config[profile] = {
        'region': region, 'adfs_netid': net_id
    }
    with open(file, 'w') as configfile:
        config.write(configfile)


def load_last_netid(file, profile):
    config = open_config_file(file)
    if config.has_section(profile) and config.has_option(profile, 'adfs_netid'):
        return config[profile]['adfs_netid']
    else:
        return ''


if __name__ == '__main__':
    main()
