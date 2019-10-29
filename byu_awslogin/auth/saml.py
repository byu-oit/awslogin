from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import int
from future import standard_library

standard_library.install_aliases()
from builtins import object
import base64
from bs4 import BeautifulSoup
import lxml.etree as ET
import requests

default_session_duration = 3600


class SAMLAssertion(object):
    def __init__(self, assertion):
        self.assertion = assertion

    def get_decoded_assertion(self):
        return ET.fromstring(base64.b64decode(self.assertion))

    def get_principal_roles(self):
        # Find all roles offered by the assertion
        raw_roles = self.get_decoded_assertion().findall(
            './/{*}Attribute[@Name="https://aws.amazon.com/SAML/Attributes/Role"]/{*}AttributeValue'
        )
        aws_roles = [element.text.split(",") for element in raw_roles]

        # Note the format of the attribute value is provider_arn, role_arn
        principal_roles = [role for role in aws_roles if ":saml-provider/" in role[0]]
        return principal_roles

    def get_session_duration(self):
        aws_session_duration = default_session_duration
        # Retrieve session duration
        for element in self.get_decoded_assertion().findall(
            './/{*}Attribute[@Name="https://aws.amazon.com/SAML/Attributes/SessionDuration"]/{*}AttributeValue'
        ):
            aws_session_duration = int(element.text)
        return aws_session_duration


def get_saml_assertion(adfs_auth_result):
    headers = {
        "Accept-Language": "en",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "text/plain, */*; q=0.01",
    }

    roles_page_response = adfs_auth_result.session.post(
        adfs_auth_result.action_url,
        verify=True,
        headers=headers,
        allow_redirects=True,
        data={
            "AuthMethod": "DuoAdfsAdapter",
            "Context": adfs_auth_result.context,
            "sig_response": adfs_auth_result.signed_response,
        },
    )

    if roles_page_response.status_code != 200:
        raise RuntimeError(
            "Issues during redirection to aws roles page. The error response {}".format(
                roles_page_response
            )
        )

    roles_page_html_soup = BeautifulSoup(roles_page_response.text, "lxml")
    return _extract_saml_assertion(roles_page_html_soup)


def get_account_names(saml_assertion):
    saml_url = "https://signin.aws.amazon.com:443/saml"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    response = requests.post(
        saml_url, headers=headers, data={"SAMLResponse": saml_assertion.assertion}
    )
    response.raise_for_status()
    html_response = BeautifulSoup(response.text, "lxml")
    account_names = {}
    for element in html_response.find_all("div", class_="saml-account-name"):
        try:
            account_id = element.text.split(" ")[2].replace("(", "").replace(")", "")
        except IndexError:
            account_id = element.text.split(" ")[1]
        account_name = element.text.split(" ")[1]
        account_names[account_id] = account_name

    return account_names


def _extract_saml_assertion(saml_page_html_soup):
    hidden_form = saml_page_html_soup.find("form", {"name": "hiddenform"})
    if not hidden_form:
        return None

    # Retrieve Base64-encoded SAML assertion from form SAMLResponse input field
    assertion = hidden_form.find("input", {"name": "SAMLResponse"})["value"]

    # If we did not get an error, but also do not have an assertion,
    # then the user needs to authenticate
    if not assertion:
        print("Unknown error: No assertion returned")
        exit(1)

    return SAMLAssertion(assertion)
