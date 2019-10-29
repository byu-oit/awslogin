#!/usr/bin/env python3
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library

standard_library.install_aliases()
import platform
import sys
import os

import click

from .__version__ import __version__
from .util.consoleeffects import Colors
from .util.data_cache import load_role_cache

try:
    import lxml.etree as ET
except ImportError:
    if platform.system() == "Windows":
        print(
            "awslogin will not run on your machine yet.  Please follow the instructions at https://github.com/byu-oit/awslogin/releases/tag/lxml to get it running."
        )
        sys.exit(1)
    else:
        raise


from .util.data_cache import get_status, load_cached_adfs_auth, remove_cached_adfs_auth
from .login import cached_login, non_cached_login


# Enable VT Mode on windows terminal code from:
# https://bugs.python.org/issue29059
# This works not sure if it the best way or not
if platform.system().lower() == "windows":
    from ctypes import windll, c_int, byref

    stdout_handle = windll.kernel32.GetStdHandle(c_int(-11))
    mode = c_int(0)
    windll.kernel32.GetConsoleMode(c_int(stdout_handle), byref(mode))
    mode = c_int(mode.value | 4)
    windll.kernel32.SetConsoleMode(c_int(stdout_handle), mode)

completion = load_role_cache()


def account_completion(ctx, args, incomplete):
    try:
        return [k for k in completion.keys() if incomplete in k]
    except:  # noqa: E722
        return []


def role_completion(ctx, args, incomplete):
    try:
        return [k for k in completion[args[1]] if incomplete in k]
    except IndexError:
        return []


@click.command()
@click.version_option(version=__version__)
@click.option(
    "-a", "--account", help="Account to login with", autocompletion=account_completion
)
@click.option(
    "-r", "--role", help="Role to use after login", autocompletion=role_completion
)
@click.option(
    "-p",
    "--profile",
    default="default",
    help="Profile to use store credentials. Defaults to default",
)
@click.option(
    "--region", default="us-west-2", help="The AWS region you will be hitting"
)
@click.option(
    "-s",
    "--status",
    is_flag=True,
    default=False,
    help="Display current logged in status. Use profile all to see all statuses",
)
@click.option(
    "--logout",
    is_flag=True,
    default=False,
    help="Logout of ADFS cached session only. Does not log out of any active profiles.",
)
@click.option("--proxy", default="", help="Specify http/https proxy to use for login")
def cli(account, role, profile, region, status, logout, proxy):
    # Display status and exit if the user specified the "-s" flag
    if status:
        get_status(profile)
        return

    if logout:
        remove_cached_adfs_auth()
        print("{}Terminated ADFS Session{}".format(Colors.yellow, Colors.normal))
        return

    if proxy:
        os.environ["http_proxy"] = proxy
        os.environ["HTTP_PROXY"] = proxy
        os.environ["https_proxy"] = proxy
        os.environ["HTTPS_PROXY"] = proxy

    # Use cached SAML assertion if already logged in, else login to ADFS
    adfs_auth_result = load_cached_adfs_auth()
    if adfs_auth_result:
        cached_login(account, role, profile, region, adfs_auth_result)
        pass
    else:
        non_cached_login(account, role, profile, region)


if __name__ == "__main__":
    cli()
