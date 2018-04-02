from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import range
from builtins import input
from builtins import int
from builtins import str
from future import standard_library
standard_library.install_aliases()
from builtins import object
import boto3
import botocore
from botocore import client

from ..util.consoleeffects import Colors


class AccountRole(object):
    def __init__(self, account_name, role_name, role_arn, principal_arn):
        self.account_name = account_name
        self.role_name = role_name
        self.role_arn = role_arn
        self.principal_arn = principal_arn


def ask_which_role_to_assume(account_names, principal_roles, account_name=None, role_name=None):
    roles_by_account = __get_roles_by_account(account_names, principal_roles)

    # User wants to assume a role on all accounts
    if account_name == 'all':
        return __get_all_account_roles(roles_by_account, role_name)
    # User wants to assume a role in a single account
    else:
        return __get_single_account_role(roles_by_account, account_name, role_name)


def assume_role(account_role, samlAssertion, sessionDuration):
    conn = boto3.client('sts', config=client.Config(signature_version=botocore.UNSIGNED))
    aws_session_token = conn.assume_role_with_saml(
        RoleArn=account_role.role_arn,
        PrincipalArn=account_role.principal_arn,
        SAMLAssertion=samlAssertion,
        DurationSeconds=sessionDuration
    )

    return aws_session_token


def __get_all_account_roles(roles_by_account, role_name):
    if not role_name:
        print("{}You must specify a role using the {}--role{} option when assuming a role accross all accounts{}".format(Colors.lred,Colors.red,Colors.lred,Colors.normal))
        exit(1)
    account_roles = []
    for account_name in roles_by_account:
        if role_name in roles_by_account[account_name]:
            account_roles.append(roles_by_account[account_name][role_name])
        else:
            print("{}Will not try to assume role '{}{}{}' in account '{}{}{}' because you don't have access to that role{}".format(Colors.lyellow,Colors.cyan,role_name,Colors.lyellow,Colors.yellow,account_name,Colors.lyellow,Colors.normal))
    return account_roles


def __get_single_account_role(roles_by_account, account_name, role_name):
    # Prompt the user for account (if not already provided)
    if not account_name or not roles_by_account[account_name]:
        account_names = list(roles_by_account.keys())
        account_names.sort()
        account_name = __prompt_for_account(account_names)
    # Prompt the user for role (if not already provided)
    if not role_name or not roles_by_account[account_name][role_name]:
        role_names = __get_role_names_for_account(roles_by_account, account_name)
        role_names.sort()
        if len(role_names) == 1:
            role_name = role_names[0]
        else:
            role_name = __prompt_for_role(account_name, role_names)

    return [roles_by_account[account_name][role_name]]  # TODO - Return real list at some point


def __get_role_names_for_account(roles_by_account, account_name):
    role_names = []
    for role_name in roles_by_account[account_name]:
        role_names.append(role_name)
    return role_names

    
def __get_roles_by_account(account_names, principal_roles):
    roles_by_account = {}
    for (principal_arn, role_arn) in principal_roles:
        account_id = role_arn.split(':')[4]
        account_name = account_names[account_id]
        role_name = role_arn.split(':')[5].split('/')[1]

        roles_by_account.setdefault(account_name, {})[role_name] = AccountRole(account_name, role_name, role_arn, principal_arn)
    return roles_by_account


def __prompt_for_account(account_names):
    print('{}#--------------------------------------------------#'.format(Colors.lblue))
    print('#     {}To which account would you like to login?{}    #'.format(Colors.white,Colors.lblue))
    print('#--------------------------------------------------#{}'.format(Colors.normal))
    
    for index, account_name in enumerate(account_names):
        print("\t{}{}{}  {}{}".format(Colors.white,str(index).rjust(2), Colors.yellow,account_name,Colors.normal))
        
    while True:
        choice = input('{}Select account:{} '.format(Colors.lblue,Colors.normal))
        try:
            return account_names[int(choice)]
        except:
            maximum = len(account_names) - 1
            print('{}Please enter an integer between 0 and {}{}'.format(Colors.lred,maximum,Colors.normal))


def __prompt_for_role(account_name, role_names):
    border = ""
    spaces = ""
    for index in range(len(account_name)):
        border = "-" + border
        spaces = " " + spaces

    print('{}#------------------------------------------------{}#'.format(Colors.lblue,border))
    print('#   {}You have access to the following roles in {}{}{}   #'.format(Colors.white,Colors.yellow,account_name,Colors.lblue))
    print('#   {}Which role would you like to assume?{}{}         #'.format(Colors.white,Colors.lblue,spaces))
    print('#------------------------------------------------{}#{}'.format(border,Colors.normal))
    
    for index, role_name in enumerate(role_names):
        if role_name == "AccountAdministrator":
            print("\t{}{}  {}{}".format(Colors.red, str(index).rjust(2), role_name,Colors.normal))
        else:
            print("\t{}{}{}  {}{}".format(Colors.white, str(index).rjust(2), Colors.cyan, role_name, Colors.normal))
    
    while True:
        choice = input('{}Select role: {}'.format(Colors.lblue, Colors.normal))
        try:
            return role_names[int(choice)]
        except:
            maximum = len(role_names) - 1
            print('{}Please enter an integer between 0 and {}{}'.format(Colors.lred, maximum, Colors.normal))
    
