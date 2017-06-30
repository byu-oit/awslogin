import boto3
import botocore
from botocore import client

def _get_roles_by_account(account_names, principal_roles):
    index = 0
    roles_by_account = {}
    for (principal_arn, role_arn) in principal_roles:
        account_id = role_arn.split(':')[4]
        account_name = account_names[account_id]
        account_role = role_arn.split(':')[5].split('/')[1]

        if not roles_by_account.get(account_name):
            roles_by_account[account_name] = {}

        roles_by_account[account_name][account_role] = {}
        roles_by_account[account_name][account_role]['index'] = index
        index += 1
    return roles_by_account


def ask_which_role_to_assume(account_names, principal_roles):
    print("#--------------------------------------------------")
    print("# Which role would you like to assume? ")
    print("#--------------------------------------------------")

    roles_by_account = _get_roles_by_account(account_names, principal_roles)

    for account_name in roles_by_account:
        print('{}:'.format(account_name))
        for account_role in roles_by_account[account_name]:
            index = roles_by_account[account_name][account_role]['index']
            print('  {} - {}'.format(account_role, index))
        print()

    role_index = int(input("Select role: "))
    return principal_roles[role_index]


def assume_role(roleArn, principalArn, samlAssertion):
    conn = boto3.client('sts', config=client.Config(signature_version=botocore.UNSIGNED))
    aws_session_token = conn.assume_role_with_saml(
        RoleArn=roleArn,
        PrincipalArn=principalArn,
        SAMLAssertion=samlAssertion,
        DurationSeconds=3600,
    )
    
    return aws_session_token


def prompt_for_account(account_names):
    print('#--------------------------------------------------')
    print('# To which account would you like to login?')
    print('#--------------------------------------------------')
    
    for index, account_name in enumerate(account_names):
        print('{} {}'.format(str(index).rjust(2)), account_name)
        
    choice = input('Select account: ')
    return account_names[int(choice)]
        