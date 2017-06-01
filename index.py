#!/usr/bin/python

import getpass

from awslogin.adfs_auth import authenticate
from awslogin.assume_role import ask_which_role_to_assume, assume_role
from awslogin.roles import action_url_on_validation_success, retrieve_roles_page

# Get the federated credentials from the user
net_id = input('BYU Net ID: ')
username = '{}@byu.local'.format(net_id)
password = getpass.getpass()
print('')

####
# Authenticate against ADFS with DUO MFA
####
html_response, session, auth_signature, duo_request_signature = authenticate(username, password)

####
# Obtain the roles available to assume
####
roles_page_url = action_url_on_validation_success(html_response)
principal_roles, assertion, aws_session_duration = retrieve_roles_page(
    roles_page_url,
    html_response,
    auth_signature,
    duo_request_signature,
)

####
# Ask user which role to assume
####
chosen_principal_role = ask_which_role_to_assume(principal_roles)

####
# Assume role and set in the environment
####
assume_role(chosen_principal_role[1], chosen_principal_role[0], assertion)
print("Assuming role: ")
print(chosen_principal_role[1])
exit(0)

# Overwrite and delete the credential variables, just for safety
username = '##############################################'
password = '##############################################'
del username
del password

print("Finished getting credentials")
