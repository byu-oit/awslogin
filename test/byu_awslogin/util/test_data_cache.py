from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import configparser
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock

from byu_awslogin.util import data_cache

tmp_aws_dir = "{}/.aws".format(tempfile.gettempdir())


def setup_module(module):
    os.makedirs(tmp_aws_dir)


def teardown_module(module):
    shutil.rmtree(tmp_aws_dir)


def read_config_file(file):
    config = configparser.ConfigParser()
    config.read(file)
    return config


@patch('byu_awslogin.util.data_cache._aws_file')
@patch('byu_awslogin.util.data_cache.os.path.exists')
def test_cache_adfs_auth(mock_exists, mock_aws_file):
    mock_exists.return_value = True
    creds_file = "{}/credentials".format(tmp_aws_dir)
    mock_aws_file.return_value = creds_file

    test_adfs_auth_val = b"testing\ntesting"
    data_cache.cache_adfs_auth(test_adfs_auth_val)

    assert test_adfs_auth_val == data_cache.load_cached_adfs_auth()


@patch('byu_awslogin.util.data_cache._aws_file')
@patch('byu_awslogin.util.data_cache.os.path.exists')
def test_remove_cached_adfs_auth(mock_exists, mock_aws_file):
    mock_exists.return_value = True
    creds_file = "{}/credentials".format(tmp_aws_dir)
    mock_aws_file.return_value = creds_file

    test_adfs_auth_val = b"testing\ntesting"
    data_cache.cache_adfs_auth(test_adfs_auth_val)
    data_cache.remove_cached_adfs_auth()

    written_config = read_config_file(creds_file)

    assert mock_exists.call_count == 1
    assert mock_aws_file.call_count == 2
    assert not written_config.has_option('all', 'adfs_auth')


@patch('byu_awslogin.util.data_cache._aws_file')
@patch('byu_awslogin.util.data_cache.os.path.exists')
def test_write_to_cred_file(mock_exists, mock_aws_file):
    mock_exists.return_value = True
    creds_file = "{}/credentials".format(tmp_aws_dir)
    mock_aws_file.return_value = creds_file

    profile = "default"
    aws_session_token = {
        'Credentials': {'AccessKeyId': 'keyid', 'SecretAccessKey': 'secretkey', 'SessionToken': 'sessiontoken'}}
    data_cache.write_to_cred_file(profile, aws_session_token)
    written_config = read_config_file(creds_file)

    assert mock_exists.call_count == 1
    assert mock_aws_file.call_count == 1
    assert written_config['default'] == {'aws_access_key_id': 'keyid',
                                         'aws_secret_access_key': 'secretkey',
                                         'aws_session_token': 'sessiontoken'
                                         }


@patch('byu_awslogin.util.data_cache._aws_file')
@patch('byu_awslogin.util.data_cache.os.path.exists')
def test_write_to_config_file(mock_exists, mock_aws_file):
    mock_exists.return_value = True
    config_file = "{}/config".format(tmp_aws_dir)
    mock_aws_file.return_value = config_file

    net_id = 'fake_netid'
    region = 'fakeRegion'
    role = 'FakeRole'
    account = 'FakeAccount'
    profile = "default"
    data_cache.write_to_config_file(profile, net_id, region, role, account, 3600)
    written_config = read_config_file(config_file)

    assert mock_exists.call_count == 1
    assert mock_aws_file.call_count == 1
    assert written_config.has_section('default')
    assert written_config.has_option('default', 'region')
    assert written_config.has_option('default', 'adfs_netid')
    assert written_config.has_option('default', 'adfs_role')
    assert written_config.has_option('default', 'adfs_expires')


@patch('byu_awslogin.util.data_cache._open_config_file')
def test_load_last_netid(mock_open_config_file):
    mock_config_file = mock_open_config_file.return_value = MagicMock()
    mock_config_file.has_section.return_value = True
    mock_config_file.has_option.return_value = True
    d = {'default': {'adfs_netid': 'fake_netid'}}
    mock_config_file.__getitem__.side_effect = d.__getitem__

    profile = "default"
    assert data_cache.load_last_netid(profile) == 'fake_netid'
    assert mock_open_config_file.call_count == 1
    assert mock_config_file.has_section.call_count == 1
    assert mock_config_file.has_option.call_count == 1
    assert mock_config_file.__getitem__.call_count == 1


@patch('byu_awslogin.util.data_cache._open_config_file')
def test_get_status(mock_open_config_file):
    mock_config_file = mock_open_config_file.return_value = MagicMock()
    d = {'default': {'adfs_role': 'fake_role', 'adfs_expires': '01-02-2017 15:03'}}
    mock_config_file.__getitem__.side_effect = d.__getitem__
    mock_config_file.has_section.return_value = True
    mock_config_file.has_option.return_value = True

    profile = "default"
    data_cache.get_status(profile)

    assert mock_open_config_file.call_count == 1
    assert mock_config_file.has_section.call_count == 1
    assert mock_config_file.has_option.call_count == 2
    assert mock_config_file.__getitem__.call_count == 3
