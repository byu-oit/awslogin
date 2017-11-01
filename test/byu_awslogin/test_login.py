from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from unittest.mock import patch, MagicMock

from byu_awslogin.login import non_cached_login, cached_login
from byu_awslogin.auth.saml import SAMLAssertion
from byu_awslogin.auth.assume_role import AccountRole
from byu_awslogin.auth.adfs_auth import AdfsAuthResult

@patch('byu_awslogin.login.get_saml_assertion')
@patch('byu_awslogin.login._prompt_for_roles_to_assume')
@patch('byu_awslogin.login.assume_role')
@patch('byu_awslogin.login.write_to_cred_file')
@patch('byu_awslogin.login.write_to_config_file')
@patch('byu_awslogin.login.cache_adfs_auth')
def test_cached_login(mock_cache_adfs_auth, mock_write_to_config_file,
                      mock_write_to_cred_file, mock_assume_role,
                      mock_prompt_roles, mock_get_saml_assertion):
    mock_get_saml_assertion.return_value = SAMLAssertion("FakeAssertion")
    mock_prompt_roles.return_value = [
        AccountRole("FakeAccount1", "FakeRole1", "FakeArn1", "FakePrincipalArn"),
        AccountRole("FakeAccount2", "FakeRole2", "FakeArn2", "FakePrincipalArn")
    ]
    mock_assume_role.return_value = "FakeSessionToken"

    cached_login("FakeAccount", None, "default", {}, 'us-west-2')

    assert mock_get_saml_assertion.call_count == 1
    assert mock_prompt_roles.call_count == 1
    assert mock_assume_role.call_count == 2
    assert mock_write_to_cred_file.call_count == 2
    assert mock_write_to_config_file.call_count == 2
    assert mock_cache_adfs_auth.call_count == 1


@patch('byu_awslogin.login._get_user_ids')
@patch('byu_awslogin.login.getpass.getpass')
@patch('byu_awslogin.login.authenticate')
@patch('byu_awslogin.login.get_saml_assertion')
@patch('byu_awslogin.login._prompt_for_roles_to_assume')
@patch('byu_awslogin.login.assume_role')
@patch('byu_awslogin.login.write_to_cred_file')
@patch('byu_awslogin.login.write_to_config_file')
@patch('byu_awslogin.login.cache_adfs_auth')
def test_non_cached_login(mock_cache_adfs_auth, mock_write_to_config_file,
                          mock_write_to_cred_file, mock_assume_role,
                          mock_prompt_roles, mock_get_saml_assertion,
                          mock_authenticate, mock_get_password, mock_get_user_ids):
    mock_get_user_ids.return_value = "FakeNetId", "FakeUsername"
    mock_get_password.return_value = "FakePassword"
    mock_authenticate.return_value = AdfsAuthResult("FakeUrl", "FakeContext", "FakeResponse", "FakeSession")
    mock_get_saml_assertion.return_value = SAMLAssertion("FakeAssertion")
    mock_prompt_roles.return_value = [
        AccountRole("FakeAccount1", "FakeRole1", "FakeArn1", "FakePrincipalArn"),
        AccountRole("FakeAccount2", "FakeRole2", "FakeArn2", "FakePrincipalArn")
    ]
    mock_assume_role.return_value = "FakeSessionToken"

    non_cached_login("FakeAccount", None, "default", 'us-west-2')

    assert mock_get_user_ids.call_count == 1
    assert mock_get_password.call_count == 1
    assert mock_authenticate.call_count == 1
    assert mock_get_saml_assertion.call_count == 1
    assert mock_prompt_roles.call_count == 1
    assert mock_assume_role.call_count == 2
    assert mock_write_to_cred_file.call_count == 2
    assert mock_write_to_config_file.call_count == 2
    assert mock_cache_adfs_auth.call_count == 1