#!/usr/bin/env python3

import getpass
import os
import subprocess

from .adfs_auth import authenticate
from .assume_role import ask_which_role_to_assume, assume_role
from .roles import action_url_on_validation_success, retrieve_roles_page

def cli():
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
    account_names, principal_roles, assertion, aws_session_duration = retrieve_roles_page(
        roles_page_url,
        html_response,
        session,
        auth_signature,
        duo_request_signature,
    )
    
    ####
    # Ask user which role to assume
    ####
    #print(principal_roles)
    chosen_principal_role = ask_which_role_to_assume(account_names, principal_roles)
    
    ####
    # Assume role and set in the environment
    ####
    aws_session_token = assume_role(chosen_principal_role[1], chosen_principal_role[0], assertion)
        
    subprocess.check_call('aws configure set aws_access_key_id {}'.format(aws_session_token['Credentials']['AccessKeyId']), shell=True)
    subprocess.check_call('aws configure set aws_secret_access_key {}'.format(aws_session_token['Credentials']['SecretAccessKey']), shell=True)
    subprocess.check_call('aws configure set aws_session_token {}'.format(aws_session_token['Credentials']['SessionToken']), shell=True)
    subprocess.check_call('aws configure set region us-west-2', shell=True)
    
    #proc = subprocess.Popen(args, env=os.environ)
    
    # Overwrite and delete the credential variables, just for safety
    username = '##############################################'
    password = '##############################################'
    del username
    del password
    
if __name__ == '__main__':
    cli()