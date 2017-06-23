import base64
from bs4 import BeautifulSoup
import lxml.etree as ET
import re
import requests

default_session_duration = 3600


_headers = {
    'Accept-Language': 'en',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'text/plain, */*; q=0.01',
}

def extract(saml_page_html_soup):
    # Retrieve Base64-encoded SAML assertion from form SAMLResponse input field
    saml_assertion = saml_page_html_soup.find('form', {"name":"hiddenform"}).find('input', {"name":"SAMLResponse"})['value']

    # If we did not get an error, but also do not have an assertion,
    # then the user needs to authenticate
    if not saml_assertion:
        print("Unknown error: No assertion returned")
        exit(1)

    # Parse the returned assertion and extract the authorized roles
    saml = ET.fromstring(base64.b64decode(saml_assertion))

    # Find all roles offered by the assertion
    raw_roles = saml.findall(
        './/{*}Attribute[@Name="https://aws.amazon.com/SAML/Attributes/Role"]/{*}AttributeValue'
    )
    aws_roles = [element.text.split(',') for element in raw_roles]

    # Note the format of the attribute value is provider_arn, role_arn
    principal_roles = [role for role in aws_roles if ':saml-provider/' in role[0]]

    aws_session_duration = default_session_duration
    # Retrieve session duration
    for element in saml.findall('.//{*}Attribute[@Name="https://aws.amazon.com/SAML/Attributes/SessionDuration"]/{*}AttributeValue'):
        aws_session_duration = int(element.text)
        
    account_names = _get_account_names(saml_assertion)

    return account_names, principal_roles, saml_assertion, aws_session_duration


def action_url_on_validation_success(login_response_html_soup):
    options_form = login_response_html_soup.find('form', id='options')
    return options_form['action']


def retrieve_roles_page(roles_page_url, login_response_html_soup, session, auth_signature, duo_request_signature):
    context = _context(login_response_html_soup)
    signed_response = '{}:{}'.format(auth_signature, _app(duo_request_signature))
    roles_page_response = session.post(
        roles_page_url,
        verify=True,
        headers=_headers,
        allow_redirects=True,
        data={
            'AuthMethod': 'DuoAdfsAdapter',
            'Context': context,
            'sig_response': signed_response,
        }
    )

    if roles_page_response.status_code != 200:
        raise RuntimeError(
            u'Issues during redirection to aws roles page. The error response {}'.format(
                roles_page_response
            )
        )

    roles_page_html_soup = BeautifulSoup(roles_page_response.text, 'lxml')
    return extract(roles_page_html_soup)


def _get_account_names(saml_assertion):
    saml_url = "https://signin.aws.amazon.com:443/saml"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    response = requests.post(saml_url, headers=headers, data={
        'SAMLResponse': saml_assertion
    })
    response.raise_for_status()
    html_response = ET.fromstring(response.text, ET.HTMLParser())
    account_names = {}
    for element in html_response.findall('.//div[@class="saml-account-name"]'):
        account_id = element.text.split(' ')[2].replace('(', '').replace(')', '')
        account_name = element.text.split(' ')[1]
        account_names[account_id] = account_name
    
    return account_names
    

def _app(request_signature):
    app_pattern = re.compile(".*(APP\|[^:]+)")
    m = app_pattern.search(request_signature)
    return m.group(1)


def _context(login_response_html_soup):
    context_input = login_response_html_soup.find('input', id='context')
    return context_input['value']
