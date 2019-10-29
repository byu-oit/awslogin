from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import input
from future import standard_library

standard_library.install_aliases()
import getpass

from .auth.adfs_auth import authenticate
from .auth.assume_role import ask_which_role_to_assume
from .auth.assume_role import assume_role
from .auth.saml import get_account_names, get_saml_assertion
from .util.consoleeffects import Colors
from .util.data_cache import (
    load_last_netid,
    write_to_config_file,
    write_to_cred_file,
    cache_adfs_auth,
)

STS_SESSION_TIMEOUT = 32400  # Valid for 9 hours


def cached_login(account, role, profile, region, adfs_auth_result):
    saml_assertion = get_saml_assertion(adfs_auth_result)

    if not saml_assertion:  # Not logged in anymore, so need to re-login
        non_cached_login(account, role, profile, region)
    else:  # Still logged in and got a SAML assertion properly
        _perform_login(
            adfs_auth_result, saml_assertion, account, role, profile, None, region
        )


def non_cached_login(account, role, profile, region):
    # Get the federated credentials from the user
    net_id, username = _get_user_ids(profile)
    password = getpass.getpass()
    print("")

    ####
    # Authenticate against ADFS with DUO MFA
    ####
    adfs_auth_result = authenticate(username, password)

    # Overwrite and delete the credential variables, just for safety
    username = "##############################################"
    password = "##############################################"
    del username
    del password

    saml_assertion = get_saml_assertion(adfs_auth_result)
    _perform_login(
        adfs_auth_result, saml_assertion, account, role, profile, net_id, region
    )


def _perform_login(
    adfs_auth_result, saml_assertion, account, role, profile, net_id, region
):
    account_roles_to_assume = _prompt_for_roles_to_assume(saml_assertion, account, role)

    # Assume all requested roles and set in the environment
    for account_role_to_assume in account_roles_to_assume:
        aws_session_token = assume_role(
            account_role_to_assume, saml_assertion.assertion, STS_SESSION_TIMEOUT
        )

        # If assuming roles across all accounts, then use the account name as the profile name
        if account == "all":
            profile = account_role_to_assume.account_name

        write_to_cred_file(profile, aws_session_token)
        write_to_config_file(
            profile,
            net_id,
            region,
            account_role_to_assume.role_name,
            account_role_to_assume.account_name,
            STS_SESSION_TIMEOUT,
        )
        _print_status_message(account_role_to_assume)

    # By caching the ADFS auth information we can re-assume roles without reauthenticating until the ADFS session expires
    cache_adfs_auth(adfs_auth_result)


def _prompt_for_roles_to_assume(saml_assertion, account, role):
    account_names = get_account_names(saml_assertion)
    account_roles_to_assume = ask_which_role_to_assume(
        account_names, saml_assertion.get_principal_roles(), account, role
    )
    return account_roles_to_assume


def _print_status_message(assumed_role):
    if assumed_role.role_name == "Admin":
        print(
            "Now logged into {}{}{}@{}{}{}".format(
                Colors.red,
                assumed_role.role_name,
                Colors.white,
                Colors.yellow,
                assumed_role.account_name,
                Colors.normal,
            )
        )
    else:
        print(
            "Now logged into {}{}{}@{}{}{}".format(
                Colors.cyan,
                assumed_role.role_name,
                Colors.white,
                Colors.yellow,
                assumed_role.account_name,
                Colors.normal,
            )
        )


def _get_user_ids(profile):
    # Ask for NetID, or use cached if user doesn't specify another
    cached_netid = load_last_netid(profile)
    if cached_netid:
        net_id_prompt = "BYU Net ID [{}{}{}]: ".format(
            Colors.blue, cached_netid, Colors.normal
        )
    else:
        net_id_prompt = "BYU Net ID: "
    net_id = input(net_id_prompt) or cached_netid

    # Append the ADFS-required "@byu.local" to the Net ID
    if "@byu.local" in net_id:
        print("{}@byu.local{} is not required".format(Colors.lblue, Colors.normal))
        username = net_id
    else:
        username = "{}@byu.local".format(net_id)

    return net_id, username
