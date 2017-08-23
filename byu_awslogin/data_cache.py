import configparser
import os
from os.path import expanduser
import datetime
from .consoleeffects import Colors


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
            print(f"{Colors.red}Couldn't find profile: {profile}")
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
    config[profile] = {
        'region': region,
        'adfs_netid': net_id,
        'adfs_role': f'{role}@{account}',
        'adfs_expires': expires.strftime('%m-%d-%Y %H:%M')
    }
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
        return f"{account_name} {Colors.white}- {expires_msg}"
    else:
        return f"{Colors.red}Couldn't find status info"


def _check_expired(expires):
    expires = datetime.datetime.strptime(expires, '%m-%d-%Y %H:%M')
    if expires > datetime.datetime.now():
        return 'Expires'
    else:
        return 'Expired'