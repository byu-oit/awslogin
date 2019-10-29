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
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.validation import Validator

from ..util.consoleeffects import Colors
from ..util.data_cache import write_role_cache


class AccountRole(object):
    def __init__(self, account_name, role_name, role_arn, principal_arn):
        self.account_name = account_name
        self.role_name = role_name
        self.role_arn = role_arn
        self.principal_arn = principal_arn


def ask_which_role_to_assume(
    account_names, principal_roles, account_name=None, role_name=None
):
    roles_by_account = __get_roles_by_account(account_names, principal_roles)

    # User wants to assume a role on all accounts
    if account_name == "all":
        return __get_all_account_roles(roles_by_account, role_name)
    # User wants to assume a role in a single account
    else:
        return __get_single_account_role(roles_by_account, account_name, role_name)


def assume_role(account_role, samlAssertion, sessionDuration):
    conn = boto3.client(
        "sts", config=client.Config(signature_version=botocore.UNSIGNED)
    )
    aws_session_token = conn.assume_role_with_saml(
        RoleArn=account_role.role_arn,
        PrincipalArn=account_role.principal_arn,
        SAMLAssertion=samlAssertion,
        DurationSeconds=sessionDuration,
    )

    return aws_session_token


def __get_all_account_roles(roles_by_account, role_name):
    if not role_name:
        print(
            "{}You must specify a role using the {}--role{} option when assuming a role accross all accounts{}".format(
                Colors.lred, Colors.red, Colors.lred, Colors.normal
            )
        )
        exit(1)
    account_roles = []
    for account_name in roles_by_account:
        if role_name in roles_by_account[account_name]:
            account_roles.append(roles_by_account[account_name][role_name])
        else:
            print(
                "{}Will not try to assume role '{}{}{}' in account '{}{}{}' because you don't have access to that role{}".format(
                    Colors.lyellow,
                    Colors.cyan,
                    role_name,
                    Colors.lyellow,
                    Colors.yellow,
                    account_name,
                    Colors.lyellow,
                    Colors.normal,
                )
            )
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

    # TODO - Return real list at some point
    return [roles_by_account[account_name][role_name]]


def __get_role_names_for_account(roles_by_account, account_name):
    role_names = []
    for role_name in roles_by_account[account_name]:
        role_names.append(role_name)
    return role_names


def __get_roles_by_account(account_names, principal_roles):
    roles_by_account = {}
    for (principal_arn, role_arn) in principal_roles:
        account_id = role_arn.split(":")[4]
        account_name = account_names[account_id]
        role_name = role_arn.split(":")[5].split("/")[1]

        roles_by_account.setdefault(account_name, {})[role_name] = AccountRole(
            account_name, role_name, role_arn, principal_arn
        )
    write_role_cache(roles_by_account)
    return roles_by_account


def __prompt_for_account(account_names):
    print("{}#--------------------------------------------------#".format(Colors.lblue))
    print(
        "#     {}To which account would you like to login?{}    #".format(
            Colors.white, Colors.lblue
        )
    )
    print(
        "#          {}Start typing an account name or{}         #".format(
            Colors.white, Colors.lblue
        )
    )
    print(
        '#              {}"list" to list accounts{}             #'.format(
            Colors.white, Colors.lblue
        )
    )
    print(
        "#--------------------------------------------------#{}".format(Colors.normal)
    )

    account_names.append("list")

    def is_valid(account):
        return account in account_names

    account_completer = FuzzyWordCompleter(account_names, WORD=True)
    validator = Validator.from_callable(
        is_valid, error_message="Not a valid account", move_cursor_to_end=True
    )
    while True:
        account = prompt(
            "Account: ",
            completer=account_completer,
            complete_while_typing=True,
            validator=validator,
        )
        if account == "list":
            for account_name in account_names:
                if account_name != "list":
                    print("\t{}{}{}".format(Colors.yellow, account_name, Colors.normal))
        else:
            return account


def __prompt_for_role(account_name, role_names):
    border = ""
    spaces = ""
    for index in range(len(account_name)):
        border = "-" + border
        spaces = " " + spaces

    print(
        "{}#------------------------------------------------{}#".format(
            Colors.lblue, border
        )
    )
    print(
        "#   {}You have access to the following roles in {}{}{}   #".format(
            Colors.white, Colors.yellow, account_name, Colors.lblue
        )
    )
    print(
        "#   {}Which role would you like to assume?{}{}         #".format(
            Colors.white, Colors.lblue, spaces
        )
    )
    print(
        "#------------------------------------------------{}#{}".format(
            border, Colors.normal
        )
    )

    for role_name in role_names:
        if role_name == "Admin":
            print("\t{}{}{}".format(Colors.red, role_name, Colors.normal))
        else:
            print("\t{}{}{}".format(Colors.cyan, role_name, Colors.normal))

    def is_valid(role):
        return role in role_names

    role_completer = FuzzyWordCompleter(role_names, WORD=True)
    validator = Validator.from_callable(
        is_valid, error_message="Not a valid Role", move_cursor_to_end=True
    )

    return prompt(
        "Select role: ",
        completer=role_completer,
        complete_while_typing=True,
        validator=validator,
    )
