import base64
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

def extract(html):
    assertion = None

    # Check to see if login returned an error
    # Since we're screen-scraping the login form, we need to pull it out of a label
    for element in html.findall('.//form[@id="loginForm"]//label[@id="errorText"]'):
        if element.text is not None:
            print('Login error: {}'.format(element.text), err=True)
            exit(-1)

    # Retrieve Base64-encoded SAML assertion from form SAMLResponse input field
    for element in html.findall('.//form[@name="hiddenform"]/input[@name="SAMLResponse"]'):
        assertion = element.get('value')

    # If we did not get an error, but also do not have an assertion,
    # then the user needs to authenticate
    if not assertion:
        return None, None, None

    # Parse the returned assertion and extract the authorized roles
    saml = ET.fromstring(base64.b64decode(assertion))

    # Find all roles offered by the assertion
    raw_roles = saml.findall(
        './/{*}Attribute[@Name="https://aws.amazon.com/SAML/Attributes/Role"]/{*}AttributeValue'
    )
    aws_roles = [element.text.split(',') for element in raw_roles]

    # Note the format of the attribute value is provider_arn, role_arn
    principal_roles = [role for role in aws_roles if ':saml-provider/' in role[0]]

    aws_session_duration = default_session_duration
    # Retrieve session duration
    for element in saml.findall(
            './/{*}Attribute[@Name="https://aws.amazon.com/SAML/Attributes/SessionDuration"]/{*}AttributeValue'
    ):
        aws_session_duration = int(element.text)

    return principal_roles, assertion, aws_session_duration



def action_url_on_validation_success(html_response):
    duo_auth_method = './/form[@id="options"]'
    element = html_response.find(duo_auth_method)
    return element.get('action')

def retrieve_roles_page(roles_page_url, html_response, session, auth_signature, duo_request_signature):

    context = _context(html_response)
    signed_response = '{}:{}'.format(auth_signature, _app(duo_request_signature))
    response = session.post(
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

    if response.status_code != 200:
        raise RuntimeError(
            u'Issues during redirection to aws roles page. The error response {}'.format(
                response
            )
        )

    html_response = ET.fromstring(response.text, ET.HTMLParser())
    return extract(html_response)


_app_pattern = re.compile(".*(APP\|[^:]+)")


def _app(request_signature):
    m = _app_pattern.search(request_signature)
    return m.group(1)

def _context(html_response):
    context_query = './/input[@id="context"]'
    element = html_response.find(context_query)
    return element.get('value')