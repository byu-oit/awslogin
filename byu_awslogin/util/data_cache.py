import base64
import configparser
import datetime
import os
import pickle
from os.path import expanduser

from .consoleeffects import Colors


def load_cached_adfs_auth():
    file = _aws_file('credentials')
    config = _open_config_file(file)
    section = 'all'
    if config.has_section(section) and config.has_option(section, 'adfs_auth'):
        unpickled = pickle.loads(base64.urlsafe_b64decode(config[section]['adfs_auth'].encode()))
        return unpickled
    else:
        return None


def cache_adfs_auth(adfs_auth_result):
    _create_aws_dir_if_not_exists()
    file = _aws_file('credentials')
    config = _open_config_file(file)
    pickled = base64.urlsafe_b64encode(pickle.dumps(adfs_auth_result)).decode()
    config['all'] = {
        'adfs_auth': pickled
    }
    with open(file, 'w') as configfile:
        config.write(configfile)


def get_status(profile='default'):
    file = _aws_file("config")
    config = _open_config_file(file)
    if profile == 'all':
        for x in config:
            if x == 'DEFAULT':
                continue
            message = _get_status_message(config, x)
            print(f"{Colors.white}{x} - {message}")
        return
    else:
        if config.has_section(profile):
            message = _get_status_message(config, profile)
            print(message)
        else:
            print(f"{Colors.red}Couldn't find profile: {profile}{Colors.normal}")
        return


def load_last_netid(profile):
    file = _aws_file('config')
    config = _open_config_file(file)
    if config.has_section(profile) and config.has_option(profile, 'adfs_netid'):
        return config[profile]['adfs_netid']
    else:
        return ''


def write_to_config_file(profile, net_id, region, role, account):
    _create_aws_dir_if_not_exists()
    file = _aws_file('config')
    one_hour = datetime.timedelta(hours=1)
    expires = datetime.datetime.now() + one_hour
    config = _open_config_file(file)
    if not net_id and config[profile].get('adfs_netid'):
        net_id = config[profile]['adfs_netid']
    config[profile] = {
        'region': region,
        'adfs_role': f'{role}@{account}',
        'adfs_expires': expires.strftime('%m-%d-%Y %H:%M')
    }
    if net_id:
        config[profile]['adfs_netid'] = net_id
    with open(file, 'w') as configfile:
        config.write(configfile)


def write_to_cred_file(profile, aws_session_token):
    _create_aws_dir_if_not_exists()
    file = _aws_file('credentials')
    config = _open_config_file(file)
    config[profile] = {
        'aws_access_key_id': aws_session_token['Credentials']['AccessKeyId'],
        'aws_secret_access_key': aws_session_token['Credentials']['SecretAccessKey'],
        'aws_session_token': aws_session_token['Credentials']['SessionToken']
    }
    with open(file, 'w') as configfile:
        config.write(configfile)


def _aws_file(file_name):
    return "{}/.aws/{}".format(expanduser("~"), file_name)


def _create_aws_dir_if_not_exists(directory="{}/.aws".format(expanduser('~'))):
    if not os.path.exists(directory):
        os.makedirs(directory)


def _open_config_file(file):
    config = configparser.ConfigParser()
    config.read(file)
    return config


def _get_status_message(config, profile):
    if config.has_option(profile, 'adfs_role') and config.has_option(profile, 'adfs_expires'):
        expires = _check_expired(config[profile]['adfs_expires'])
        account_name = f"{Colors.cyan}{config[profile]['adfs_role']}"
        if expires == 'Expired':
            expires_msg = f"{Colors.red}{expires} at: {config[profile]['adfs_expires']}"
        else:
            expires_msg = f"{Colors.yellow}{expires} at: {config[profile]['adfs_expires']}"
        return f"{account_name} {Colors.white}- {expires_msg}{Colors.normal}"
    else:
        return f"{Colors.red}Couldn't find status info{Colors.normal}"


def _check_expired(expires):
    expires = datetime.datetime.strptime(expires, '%m-%d-%Y %H:%M')
    if expires > datetime.datetime.now():
        return 'Expires'
    else:
        return 'Expired'