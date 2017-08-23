#!/usr/bin/env python3


import getpass
import click
import sys
import platform
from .consoleeffects import Colors

try:
    import lxml.etree as ET
except ImportError:
    if platform.system() == 'Windows':
        print('awslogin will not run on your machine yet.  Please follow the instructions at https://github.com/byu-oit/awslogin/releases/tag/lxml to get it running.')
        sys.exit(1)
    else:
        raise

from .adfs_auth import authenticate
from .assume_role import ask_which_role_to_assume, assume_role
from .roles import retrieve_roles_page
from .data_cache import get_status, load_last_netid, write_to_config_file, write_to_cred_file

__VERSION__ = '0.11.3'

# Enable VT Mode on windows terminal code from:
# https://bugs.python.org/issue29059
# This works not sure if it the best way or not
if platform.system().lower() == 'windows':
    from ctypes import windll, c_int, byref
    stdout_handle = windll.kernel32.GetStdHandle(c_int(-11))
    mode = c_int(0)
    windll.kernel32.GetConsoleMode(c_int(stdout_handle), byref(mode))
    mode = c_int(mode.value | 4)
    windll.kernel32.SetConsoleMode(c_int(stdout_handle), mode)


@click.command()
@click.version_option(version=__VERSION__)
@click.option('-a', '--account', help='Account to login with')
@click.option('-r', '--role', help='Role to use after login')
@click.option('-p', '--profile', default='default', help='Profile to use store credentials. Defaults to default')
@click.option('-s', '--status', is_flag=True, default=False, help='Display current logged in status. Use profile all to see all statuses')
def cli(account, role, profile, status):
    _ensure_min_python_version()

    # Display status and exit if the user specified the "-s" flag
    if status:
        get_status(profile)
        return

    # Get the federated credentials from the user
    net_id, username = _get_user_ids(profile)
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
    account_names, principal_roles, assertion, aws_session_duration = retrieve_roles_page(
        html_response,
        session,
        auth_signature,
        duo_request_signature,
    )

    ####
    # Ask user which role to assume
    ####
    account_roles_to_assume = ask_which_role_to_assume(account_names, principal_roles, account, role)

    ####
    # Assume roles and set in the environment
    ####
    for account_role_to_assume in account_roles_to_assume:
        aws_session_token = assume_role(account_role_to_assume, assertion)

        # If assuming roles across all accounts, then use the account name as the profile name
        if account == 'all':
            profile = account_role_to_assume.account_name

        write_to_cred_file(profile, aws_session_token)
        write_to_config_file(profile, net_id, 'us-west-2', account_role_to_assume.role_name, account_role_to_assume.account_name)
        _print_status_message(account_role_to_assume)


def _print_status_message(assumed_role):
    if assumed_role.role_name == "AccountAdministrator":
        print("Now logged into {}{}{}@{}{}{}".format(Colors.red, assumed_role.role_name, Colors.white,
                                                     Colors.yellow, assumed_role.account_name, Colors.normal))
    else:
        print("Now logged into {}{}{}@{}{}{}".format(Colors.cyan, assumed_role.role_name, Colors.white,
                                                     Colors.yellow, assumed_role.account_name, Colors.normal))


def _get_user_ids(profile):
    # Ask for NetID, or use cached if user doesn't specify another
    cached_netid = load_last_netid(profile)
    if cached_netid:
        net_id_prompt = 'BYU Net ID [{}{}{}]: '.format(Colors.blue,cached_netid,Colors.normal)
    else:
        net_id_prompt = 'BYU Net ID: '
    net_id = input(net_id_prompt) or cached_netid

    # Append the ADFS-required "@byu.local" to the Net ID
    if "@byu.local" in net_id:
        print('{}@byu.local{} is not required'.format(Colors.lblue,Colors.normal))
        username = net_id
    else:
        username = '{}@byu.local'.format(net_id)

    return net_id, username


def _ensure_min_python_version():
    if not sys.version.startswith('3.6'):
        sys.stderr.write("{}byu_awslogin requires python 3.6{}\n".format(Colors.red, Colors.white))
        sys.exit(-1)


if __name__ == '__main__':
    cli()

