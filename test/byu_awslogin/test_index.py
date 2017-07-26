import pytest
import os.path
import configparser
import datetime
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
    exp_date = datetime.datetime.now() + datetime.timedelta(hours=1)
    if not os.path.exists(dir):
        os.makedirs(dir)
    config = configparser.ConfigParser()
    config['default'] = {
        'region': 'fake-region-1',
        'adfs_netid': 'fake_netid',
        'adfs_role': 'FakeRole@FakeAccount',
        'adfs_expires': exp_date.strftime('%m-%d-%Y %H:%M')
    }
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
    role = 'FakeRole'
    account = 'FakeAccount'
    index.write_to_config_file(aws_config_file, net_id, region, profile, role, account)
    config = read_config_file(aws_config_file)
    assert config.has_section('default')
    assert config.has_option('default', 'region')
    assert config.has_option('default', 'adfs_netid')
    assert config.has_option('default', 'adfs_role')
    assert config.has_option('default', 'adfs_expires')


def test_load_last_netid(fake_config_file, profile):
    assert index.load_last_netid(str(fake_config_file), profile) == 'fake_netid'


def test_cli_version(capfd):
    index.cli(version=True)
    out, err = capfd.readouterr()
    assert out.strip() == f'awslogin version: {index.__VERSION__}'


def test_get_status(fake_config_file, profile, capfd):
    index.get_status(str(fake_config_file), profile)
    out, err = capfd.readouterr()
    assert 'FakeRole@FakeAccount' in out


def test_get_status_fail(fake_config_file, capfd):
    index.get_status(str(fake_config_file), 'fake')
    out, err = capfd.readouterr()
    assert "Couldn't find profile:" in out


def test_check_expired():
    expired = datetime.datetime.now() - datetime.timedelta(hours=1)
    result = index.check_expired(expired.strftime('%m-%d-%Y %H:%M'))
    assert result == 'Expired'
    expires = datetime.datetime.now() + datetime.timedelta(hours=1)
    result = index.check_expired(expires.strftime('%m-%d-%Y %H:%M'))
    assert result == 'Expires'
