import boto3
import botocore
from botocore import client


class AccountRole:

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


def assume_role(account_role, samlAssertion):
    conn = boto3.client('sts', config=client.Config(signature_version=botocore.UNSIGNED))
    aws_session_token = conn.assume_role_with_saml(
        RoleArn=account_role.role_arn,
        PrincipalArn=account_role.principal_arn,
        SAMLAssertion=samlAssertion,
        DurationSeconds=3600,
    )

    return aws_session_token


def __get_all_account_roles(roles_by_account, role_name):
    if not role_name:
        print("You must speicify a role using the --role option when assuming a role accross all accounts")
        exit(1)
    account_roles = []
    for account_name in roles_by_account:
        if role_name in roles_by_account[account_name]:
            account_roles.append(roles_by_account[account_name][role_name])
        else:
            print("Will not try to assume role '{}' in account '{}' because you don't have access to that role".format(
                role_name, account_name))
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
    print('#--------------------------------------------------')
    print('# To which account would you like to login?')
    print('#--------------------------------------------------')
    
    for index, account_name in enumerate(account_names):
        print('{} {}'.format(str(index).rjust(2), account_name))
        
    while True:
        choice = input('Select account: ')
        try:
            return account_names[int(choice)]
        except:
            maximum = len(account_names) - 1
            print('Please enter an integer between 0 and {}'.format(maximum))


def __prompt_for_role(account_name, role_names):
    print('#--------------------------------------------------')
    print('# You have access to the following roles in {}'.format(account_name))
    print('# Which role would you like to assume?')
    print('#--------------------------------------------------')
    
    for index, role_name in enumerate(role_names):
        print('{} {}'.format(str(index).rjust(2), role_name))
    
    while True:
        choice = input('Select role: ')
        try:
            return role_names[int(choice)]
        except:
            maximum = len(role_names) - 1
            print('Please enter an integer between 0 and {}'.format(maximum))
    