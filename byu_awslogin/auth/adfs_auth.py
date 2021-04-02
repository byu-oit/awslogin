from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

#
# This file was adapted from https://github.com/venth/aws-adfs. Thanks to https://github.com/venth for his work on
# figuring this out
#
from builtins import object
from future import standard_library

standard_library.install_aliases()
import os
import re
import sys

try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs

import lxml.etree as ET
import requests
from bs4 import BeautifulSoup

from ..util.consoleeffects import Colors

# idpentryurl: The initial url that starts the authentication process.
adfs_entry_url = "https://awslogin.byu.edu:443/adfs/ls/IdpInitiatedSignOn.aspx?loginToRp=urn:amazon:webservices"


class AdfsAuthResult(object):
    def __init__(self, action_url, context, signed_response, session):
        self.action_url = action_url
        self.context = context
        self.signed_response = signed_response
        self.session = session


def authenticate(username, password):
    # Initiate session handler
    session = requests.Session()

    # Get the ADFS sign-in page HTML
    login_page_response = session.get(adfs_entry_url, verify=True)

    # Parse the response and extract all the necessary values
    # in order to build a dictionary of all of the form values the IdP expects
    login_html_soup = BeautifulSoup(login_page_response.text, "lxml")
    auth_payload = _get_auth_payload(login_html_soup, username, password)

    # From the form action for the login form, build the URL used to submit the login request
    adfs_form_submit_url = _get_login_submit_url(login_html_soup)

    # Login with the ADFS credentials
    login_response = session.post(adfs_form_submit_url, data=auth_payload, verify=True)

    login_response_html_soup = BeautifulSoup(login_response.text, "lxml")

    # Check that authentication succeeded. Exit with error if it didn't
    _check_adfs_authentication_success(login_response_html_soup)

    # Perform DUO MFA
    auth_signature, duo_request_signature = _authenticate_duo(
        login_response_html_soup, True, session
    )
    signed_response = _get_signed_response(auth_signature, duo_request_signature)
    context = _context(login_response_html_soup)
    action_url = _action_url_on_validation_success(login_response_html_soup)

    return AdfsAuthResult(action_url, context, signed_response, session)


_headers = {
    "Accept-Language": "en",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "text/plain, */*; q=0.01",
}


def _action_url_on_validation_success(login_response_html_soup):
    options_form = login_response_html_soup.find("form", id="options")
    return options_form["action"]


def _get_signed_response(auth_signature, duo_request_signature):
    return "{}:{}".format(auth_signature, _app(duo_request_signature))


def _app(request_signature):
    app_pattern = re.compile(".*(APP\|[^:]+)")
    m = app_pattern.search(request_signature)
    return m.group(1)


def _context(login_response_html_soup):
    context_input = login_response_html_soup.find("input", id="context")
    return context_input["value"]


def _get_auth_payload(login_html_soup, username, password):
    auth_payload = {}
    for inputtag in login_html_soup.find_all(re.compile("(INPUT|input)")):
        name = inputtag.get("name", "")
        value = inputtag.get("value", "")
        if "user" in name.lower():
            # Make an educated guess that this is the right field for the username
            auth_payload[name] = username
        elif "pass" in name.lower():
            # Make an educated guess that this is the right field for the password
            auth_payload[name] = password
        else:
            # Simply populate the parameter with the existing value (picks up hidden fields in the login form)
            auth_payload[name] = value
    return auth_payload


def _get_login_submit_url(login_html_soup):
    parsed_adfs_login_url = urlparse(adfs_entry_url)
    adfs_form_submit_url = (
        parsed_adfs_login_url.scheme + "://" + parsed_adfs_login_url.netloc
    )
    for inputtag in login_html_soup.find_all(re.compile("(FORM|form)")):
        action = inputtag.get("action")
        loginid = inputtag.get("id")
        if action and loginid == "loginForm":
            adfs_form_submit_url += action
    return adfs_form_submit_url


def _check_adfs_authentication_success(login_response_html_soup):
    login_form_tag = login_response_html_soup.find("form", id="loginForm")
    if login_form_tag:  # Login form present means the authentication failed
        auth_error = login_form_tag.find("span", id="errorText")
        print(auth_error.string)
        exit(1)


def _authenticate_duo(duo_page_html_soup, roles_page_url, session):
    duo_host = _duo_host(duo_page_html_soup)
    duo_request_signature = _duo_request_signature(duo_page_html_soup)

    print("Sending request for authentication")
    (sid, preferred_factor, preferred_device), initiated = _initiate_authentication(
        duo_host, duo_request_signature, roles_page_url, session
    )
    if initiated:
        transaction_id = _begin_authentication_transaction(
            duo_host, sid, preferred_factor, preferred_device, session
        )

        print("Waiting for additional authentication")
        _verify_that_code_was_sent(duo_host, sid, transaction_id, session)
        _verify_auth_result(duo_host, sid, transaction_id, session)
        auth_signature = _authentication_result(duo_host, sid, transaction_id, session,)

        return auth_signature, duo_request_signature
    else:
        raise RuntimeError("DUO Transaction Not Initiated")


def _authentication_result(duo_host, sid, duo_transaction_id, session):
    status_for_url = "https://{}/frame/status/{}".format(duo_host, duo_transaction_id)
    response = session.post(
        status_for_url,
        verify=True,
        headers=_headers,
        data={"sid": sid, "txid": duo_transaction_id},
    )

    if response.status_code != 200:
        raise RuntimeError(
            "Issues during retrieval of a code entered into "
            "the device. The error response {}".format(response)
        )

    json_response = response.json()
    if json_response["stat"] != "OK":
        raise RuntimeError(
            "There was an issue during retrieval of a code entered into the device."
            " The error response: {}".format(response.text)
        )
    auth_signature = response.json()["response"]["cookie"]
    return auth_signature


def _verify_auth_result(duo_host, sid, duo_transaction_id, session):
    status_for_url = "https://{}/frame/status".format(duo_host)
    response = session.post(
        status_for_url,
        verify=True,
        headers=_headers,
        data={"sid": sid, "txid": duo_transaction_id},
    )

    if response.status_code != 200:
        raise RuntimeError(
            "Issues during retrieval of a code entered into "
            "the device. The error response {}".format(response)
        )

    json_response = response.json()
    if json_response["stat"] != "OK":
        raise RuntimeError(
            "There was an issue during retrieval of a code entered into the device."
            " The error response: {}".format(response.text)
        )

    if json_response["response"]["status_code"] != "allow":
        if (
            json_response["response"]["reason"] == "User mistake"
            and json_response["response"]["status"] == "Login request denied."
        ):
            print("{}Duo Auth Denied{}".format(Colors.red, Colors.normal))
            sys.exit(1)
        raise RuntimeError(
            "There was an issue during retrieval of a code entered into the device."
            " The error response: {}".format(response.text)
        )


def _verify_that_code_was_sent(duo_host, sid, duo_transaction_id, session):
    status_for_url = "https://{}/frame/status".format(duo_host)
    response = session.post(
        status_for_url,
        verify=True,
        headers=_headers,
        data={"sid": sid, "txid": duo_transaction_id},
    )

    if response.status_code != 200:
        raise RuntimeError(
            "Issues during sending code to the devide. The error response {}".format(
                response
            )
        )

    json_response = response.json()
    if json_response["stat"] != "OK":
        raise RuntimeError(
            "There was an issue during sending code to the device. The error response: {}".format(
                response.text
            )
        )

    if json_response["response"]["status_code"] != "pushed":
        raise RuntimeError(
            "There was an issue during sending code to the device. The error response: {}".format(
                response.text
            )
        )


def _tx(request_signature):
    tx_pattern = re.compile("(TX\|[^:]+):APP.+")
    m = tx_pattern.search(request_signature)
    return m.group(1)


def _initiate_authentication(duo_host, duo_request_signature, roles_page_url, session):
    prompt_for_url = "https://{}/frame/web/v1/auth".format(duo_host)
    parent = "{}{}".format(
        roles_page_url,
        "&java_version="
        "&flash_version="
        "&screen_resolution_width=1280"
        "&screen_resolution_height=800"
        "&color_depth=24",
    )
    response = session.post(
        prompt_for_url,
        verify=True,
        headers={
            "Host": duo_host,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        allow_redirects=True,
        params={"tx": _tx(duo_request_signature), "parent": parent, "v": "2.3",},
        data={
            "parent": parent,
            "java_version": "",
            "flash_version": "22.0.0.209",
            "screen_resolution_width": "1280",
            "screen_resolution_height": "800",
            "color_depth": "24",
        },
    )

    if response.status_code != 200 or response.url is None:
        return None, False

    o = urlparse(response.url)
    query = parse_qs(o.query)

    if "sid" not in query:
        return None, False

    sid = query["sid"]
    html_response = ET.fromstring(response.text, ET.HTMLParser())
    preferred_factor = _preferred_factor(html_response)
    preferred_device = _preferred_device(html_response)
    return (sid, preferred_factor, preferred_device), True


def _preferred_factor(html_response):
    preferred_factor_query = './/input[@name="preferred_factor"]'
    element = html_response.find(preferred_factor_query)
    return element.get("value")


def _preferred_device(html_response):
    preferred_device_query = './/input[@name="preferred_device"]'
    element = html_response.find(preferred_device_query)
    return element.get("value")


def _begin_authentication_transaction(
    duo_host, sid, preferred_factor, preferred_device, session
):
    prompt_for_url = "https://{}/frame/prompt".format(duo_host)
    response = session.post(
        prompt_for_url,
        verify=True,
        headers=_headers,
        data={
            "sid": sid,
            "factor": preferred_factor,
            "device": preferred_device,
            "out_of_date": "",
        },
    )

    if response.status_code != 200:
        raise RuntimeError(
            "Issues during beginning of the authentication process. The error response {}".format(
                response
            )
        )

    json_response = response.json()
    if json_response["stat"] != "OK":
        if json_response["message"] == "Unknown authentication method.":
            print(
                "{}Generic Authentication Failure.\n{}Are you enrolled in Duo MFA?\nDid you enable Duo automatic push?{}".format(
                    Colors.lred, Colors.lyellow, Colors.normal
                )
            )
            os._exit(1)
        else:
            raise RuntimeError(
                "Cannot begin authentication process. The error response: {}".format(
                    response.text
                )
            )
    return json_response["response"]["txid"]


def _duo_host(duo_page_html_soup):
    duo_script = (
        duo_page_html_soup.find("form", id="duo_form")
        .find_next_sibling("script")
        .string
    )
    duo_host_pattern = re.compile("'host': '([^']+)'")
    m = duo_host_pattern.search(duo_script)
    return m.group(1)


def _duo_request_signature(duo_page_html_soup):
    duo_script = (
        duo_page_html_soup.find("form", id="duo_form")
        .find_next_sibling("script")
        .string
    )
    duo_signature_pattern = re.compile("'sig_request': '([^']+)'")
    m = duo_signature_pattern.search(duo_script)
    return m.group(1)
