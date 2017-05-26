#!/usr/bin/python

import boto3
import getpass
import duo_authenticator
import roles
import adfs_auth

# Get the federated credentials from the user
net_id = input('BYU Net ID: ')
username = '{}@byu.local'.format(net_id)
password = getpass.getpass()
print('')

html_response, session = adfs_auth.authenticate(username, password)

roles_page_url = roles.action_url_on_validation_success(html_response)

auth_signature = duo_authenticator.authenticate_duo(html_response, True, session)
duo_request_signature = duo_authenticator._duo_request_signature(html_response)

principal_roles, assertion, aws_session_duration = roles.retrieve_roles_page(
    roles_page_url,
    html_response,
    session,
    auth_signature,
    duo_request_signature,
)

print("PRINCIPAL ROLES")
for principal_role in principal_roles:
    print("  {}".format(principal_role))

# Overwrite and delete the credential variables, just for safety
username = '##############################################'
password = '##############################################'
del username
del password

print("Finished getting credentials")
