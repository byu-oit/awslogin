import boto3
import botocore
from botocore import client

# def _get_roles_by_account(account_names, principal_roles):
#     index = 0
#     roles_by_account = {}
#     for (principal_arn, role_arn) in principal_roles:
#         account_id = role_arn.split(':')[4]
#         account_name = account_names[account_id]
#         account_role = role_arn.split(':')[5].split('/')[1]

#         if not roles_by_account.get(account_name):
#             roles_by_account[account_name] = {}

#         roles_by_account[account_name][account_role] = {}
#         roles_by_account[account_name][account_role]['index'] = index
#         index += 1
#     return roles_by_account


def ask_which_role_to_assume(account_names, principal_roles, account_name=None, role_name=None):
    roles_by_account = get_roles_by_account(account_names, principal_roles)
    
    # Prompt the user for account (if not already provided)
    if not account_name or account_name not in roles_by_account:
        account_names = list(roles_by_account.keys())
        account_names.sort()
        account_name = prompt_for_account(account_names)
    # Prompt the user for role (if not already provided)
    if not role_name or role_name not in roles_by_account[account_name]:
        role_names = list(roles_by_account[account_name].keys())
        role_names.sort()
        if len(role_names) == 1:
            role_name = role_names[0]
        else:
            role_name = prompt_for_role(account_name, role_names)
    # Return role_arn and principal_arn for chosen role
    return account_name, role_name, roles_by_account[account_name][role_name]


def assume_role(roleArn, principalArn, samlAssertion):
    conn = boto3.client('sts', config=client.Config(signature_version=botocore.UNSIGNED))
    aws_session_token = conn.assume_role_with_saml(
        RoleArn=roleArn,
        PrincipalArn=principalArn,
        SAMLAssertion=samlAssertion,
        DurationSeconds=3600,
    )
    
    return aws_session_token
    
    
def get_roles_by_account(account_names, principal_roles):
    roles_by_account = {}
    for (principal_arn, role_arn) in principal_roles:
        account_id = role_arn.split(':')[4]
        account_name = account_names[account_id]
        account_role = role_arn.split(':')[5].split('/')[1]
        
        roles_by_account.setdefault(account_name, {})[account_role] = (role_arn, principal_arn)
    return roles_by_account


def prompt_for_account(account_names):
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


def prompt_for_role(account_name, role_names):
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
    