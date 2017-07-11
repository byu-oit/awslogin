import pytest
import os.path
import configparser
from byu_awslogin import index


@pytest.fixture
def aws_config_file(tmpdir):
    return str(tmpdir.dirpath(".aws/config"))


@pytest.fixture
def aws_cred_file(tmpdir):
    return str(tmpdir.dirpath(".aws/credentials"))


@pytest.fixture
def read_config_file(file):
    config = configparser.ConfigParser()
    config.read(file)
    return config


@pytest.fixture
def profile():
    return 'default'

@pytest.fixture
def fake_config_file(tmpdir):
    dir = tmpdir.dirpath(".aws/")
    file = dir + 'config'
    if not os.path.exists(dir):
        os.makedirs(dir)
    config = configparser.ConfigParser()
    config['default'] = {'region': 'fake-region-1', 'adfs_netid': 'fake_netid'}
    with open(file, 'w') as write_file:
        config.write(write_file)
    return file


def test_open_config_file(aws_config_file):
    assert index.open_config_file(aws_config_file)


def test_aws_file():
    assert index.aws_file('config')


def test_check_for_aws_dir(tmpdir):
    dir = tmpdir.dirpath(".aws")
    index.check_for_aws_dir(dir)
    assert os.path.exists(dir)


def test_write_to_cred_file(aws_cred_file, profile):
    aws_session_token = {'Credentials': {'AccessKeyId': 'keyid', 'SecretAccessKey': 'secretkey', 'SessionToken': 'sessiontoken'}}
    index.write_to_cred_file(aws_cred_file, aws_session_token, profile)
    config = read_config_file(aws_cred_file)
    assert config['default'] == {'aws_access_key_id': 'keyid',
                                 'aws_secret_access_key': 'secretkey',
                                 'aws_session_token': 'sessiontoken'
                                 }


def test_write_to_config_file(aws_config_file, profile):
    net_id = 'fake_netid'
    region = 'fakeRegion'
    index.write_to_config_file(aws_config_file, net_id, region, profile)
    config = read_config_file(aws_config_file)
    assert config['default'] == {'region': 'fakeRegion', 'adfs_netid': 'fake_netid'}


def test_load_last_netid(fake_config_file, profile):
    assert index.load_last_netid(str(fake_config_file), profile) == 'fake_netid'


@pytest.mark.skip(reason="not sure how to test this yet")
def test_cli():
    pass
