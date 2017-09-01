#!/usr/bin/env python3



import platform
import sys

import click

from .util.consoleeffects import Colors

try:
    import lxml.etree as ET
except ImportError:
    if platform.system() == 'Windows':
        print('awslogin will not run on your machine yet.  Please follow the instructions at https://github.com/byu-oit/awslogin/releases/tag/lxml to get it running.')
        sys.exit(1)
    else:
        raise


from .util.data_cache import get_status, load_cached_adfs_auth
from .login import cached_login, non_cached_login

__VERSION__ = '0.12.2'

# Enable VT Mode on windows terminal code from:
# https://bugs.python.org/issue29059
# This works not sure if it the best way or not
if platform.system().lower() == 'windows':
    from ctypes import windll, c_int, byref
    stdout_handle = windll.kernel32.GetStdHandle(c_int(-11))
    mode = c_int(0)
    windll.kernel32.GetConsoleMode(c_int(stdout_handle), byref(mode))
    mode = c_int(mode.value | 4)
    windll.kernel32.SetConsoleMode(c_int(stdout_handle), mode)


@click.command()
@click.version_option(version=__VERSION__)
@click.option('-a', '--account', help='Account to login with')
@click.option('-r', '--role', help='Role to use after login')
@click.option('-p', '--profile', default='default', help='Profile to use store credentials. Defaults to default')
@click.option('-s', '--status', is_flag=True, default=False, help='Display current logged in status. Use profile all to see all statuses')
def cli(account, role, profile, status):
    _ensure_min_python_version()

    # Display status and exit if the user specified the "-s" flag
    if status:
        get_status(profile)
        return

    # Use cached SAML assertion if already logged in, else login to ADFS
    adfs_auth_result = load_cached_adfs_auth()
    if adfs_auth_result:
        cached_login(account, role, profile, adfs_auth_result)
        pass
    else:
        non_cached_login(account, role, profile)


def _ensure_min_python_version():
    if not sys.version.startswith('3.6'):
        sys.stderr.write("{}byu_awslogin requires python 3.6{}\n".format(Colors.red, Colors.white))
        sys.exit(-1)


if __name__ == '__main__':
    cli()

