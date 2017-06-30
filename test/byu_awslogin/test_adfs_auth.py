from byu_awslogin.adfs_auth import authenticate
from unittest.mock import patch, MagicMock
import os
import json

@patch('byu_awslogin.adfs_auth.requests')
def test_authenticate(mock_requests):
    mock_session = mock_requests.Session.return_value = MagicMock()    
    
    # Mock initial login page
    script_dir = os.path.dirname(os.path.realpath(__file__))
    auth_page_text = open('{}/adfs_html_mocks/login_screen.html'.format(script_dir), 'r').read()
    auth_page_mock = MagicMock(status_code=200, text=auth_page_text)
    mock_session.get.side_effect = [auth_page_mock]
    
    # Mock duo required page
    duo_page_text = open('{}/adfs_html_mocks/duo_screen.html'.format(script_dir), 'r').read()
    duo_screen_mock = MagicMock(status_code=200, text=duo_page_text)
    
    # Mock duo init page
    duo_init_text = open('{}/adfs_html_mocks/duo_init.html'.format(script_dir), 'r').read()
    duo_init_url = "https://REDACTED.duosecurity.com/frame/prompt?sid=REDACTED"
    duo_init_mock = MagicMock(status_code=200, text=duo_init_text, url=duo_init_url)
    
    # Mock duo init auth transaction
    duo_auth_trans_init_json = open('{}/adfs_html_mocks/duo-trans-init.json'.format(script_dir), 'r').read()
    duo_auth_trans_init_mock = MagicMock(status_code=200, text=duo_auth_trans_init_json)
    duo_auth_trans_init_mock.json.return_value = json.loads(duo_auth_trans_init_json)
    
    # Mock duo verify code
    duo_verify_code_json = open('{}/adfs_html_mocks/duo_trans_verify.json'.format(script_dir), 'r').read()
    duo_verify_code_mock = MagicMock(status_code=200, text=duo_verify_code_json)
    duo_verify_code_mock.json.return_value = json.loads(duo_verify_code_json)
    
    # Mock duo auth result
    duo_auth_result_json = open('{}/adfs_html_mocks/duo_auth_result.json'.format(script_dir), 'r').read()
    duo_auth_result_mock = MagicMock(status_code=200, text=duo_auth_result_json)
    duo_auth_result_mock.json.return_value = json.loads(duo_auth_result_json)
    
    mock_session.post.side_effect = [duo_screen_mock, duo_init_mock, duo_auth_trans_init_mock, duo_verify_code_mock, duo_auth_result_mock]
    login_response_html_soup, session, auth_signature, duo_request_signature = authenticate('FakeUsername', 'FakePassword')
    assert auth_signature == 'REDACTED'
    assert duo_request_signature == 'TX|REDACTED:APP|REDACTED'