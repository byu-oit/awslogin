from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import pytest
from byu_awslogin import index
from click.testing import CliRunner
from unittest.mock import patch
from byu_awslogin.util.consoleeffects import Colors


@pytest.mark.skip("Not Fully Tested")
def test_cli():
    print("I NEED TO BE TESTED!")


@patch('byu_awslogin.index.get_status')
def test_cli_status(mock_status):
    results = CliRunner().invoke(index.cli, ['-s'])

    assert results.exit_code == 0
    assert mock_status.call_count == 1


@patch('byu_awslogin.index.remove_cached_adfs_auth')
def test_cli_logout(mock_remove_adfs):
    results = CliRunner().invoke(index.cli, ['--logout'])

    assert results.exit_code == 0
    assert results.output.strip() == "{}Terminated ADFS Session{}".format(Colors.yellow, Colors.normal)
    assert mock_remove_adfs.call_count == 1
