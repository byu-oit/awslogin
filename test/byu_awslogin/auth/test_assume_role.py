from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from byu_awslogin.auth.assume_role import ask_which_role_to_assume


def test_ask_which_role_to_assume_single_role():
    account_names = {
        '333333333333': 'my-dev-account',
        '222222222222': 'my-prod-account'
    }
    principal_roles = [
        ['arn:aws:iam::333333333333:saml-provider/ADFS', 'arn:aws:iam::333333333333:role/ReadOnly'],
        ['arn:aws:iam::333333333333:saml-provider/ADFS', 'arn:aws:iam::333333333333:role/Admin'],
        ['arn:aws:iam::222222222222:saml-provider/ADFS', 'arn:aws:iam::222222222222:role/ReadOnly']
    ]
    account_name = 'my-dev-account'
    role_name = "ReadOnly"

    account_roles = ask_which_role_to_assume(account_names, principal_roles, account_name, role_name)
    assert len(account_roles) == 1
    assert account_roles[0].account_name == "my-dev-account"
    assert account_roles[0].role_name == "ReadOnly"
    assert account_roles[0].principal_arn == "arn:aws:iam::333333333333:saml-provider/ADFS"
    assert account_roles[0].role_arn == "arn:aws:iam::333333333333:role/ReadOnly"

def test_ask_which_role_to_assume_all_roles():
    account_names = {
        '333333333333': 'my-dev-account',
        '222222222222': 'my-prod-account'
    }
    principal_roles = [
        ['arn:aws:iam::333333333333:saml-provider/ADFS', 'arn:aws:iam::333333333333:role/ReadOnly'],
        ['arn:aws:iam::333333333333:saml-provider/ADFS', 'arn:aws:iam::333333333333:role/Admin'],
        ['arn:aws:iam::222222222222:saml-provider/ADFS', 'arn:aws:iam::222222222222:role/ReadOnly']
    ]
    account_name = 'all'
    role_name = "ReadOnly"

    account_roles = ask_which_role_to_assume(account_names, principal_roles, account_name, role_name)
    assert len(account_roles) == 2
    assert account_roles[0].account_name == 'my-dev-account'
    assert account_roles[0].role_name == "ReadOnly"
    assert account_roles[1].account_name == "my-prod-account"
    assert account_roles[1].role_name == "ReadOnly"