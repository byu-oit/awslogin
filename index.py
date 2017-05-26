#!/usr/bin/python

import boto3
import getpass
import duo
import roles
import assume_role
import adfs_auth

# Get the federated credentials from the user
net_id = input('BYU Net ID: ')
username = '{}@byu.local'.format(net_id)
password = getpass.getpass()
print('')

####
# Authenticate against ADFS
####
html_response, session = adfs_auth.authenticate(username, password)

####
# Perform the DUO push
####
auth_signature, duo_request_signature = duo.authenticate_duo(html_response, True, session)

####
# Obtain the roles available to assume
####
roles_page_url = roles.action_url_on_validation_success(html_response)
principal_roles, assertion, aws_session_duration = roles.retrieve_roles_page(
    roles_page_url,
    html_response,
    session,
    auth_signature,
    duo_request_signature,
)

####
# Ask user which role to assume
####
chosen_principal_role = assume_role.ask_which_role_to_assume(principal_roles)

####
# Assume role and set in the environment
####
assume_role.assume_role(chosen_principal_role[1], chosen_principal_role[0], assertion)
print("Assuming role: ")
print(chosen_principal_role[1])
exit(0)

# Overwrite and delete the credential variables, just for safety
username = '##############################################'
password = '##############################################'
del username
del password

print("Finished getting credentials")
