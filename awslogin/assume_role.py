import boto3
import botocore
from botocore import client

def ask_which_role_to_assume(principal_roles):
    print("Which role would you like to assume? ")
    index =  0
    for (principal_arn, role_arn) in principal_roles:
        print("  {} - {}".format(index, role_arn))
        index += 1
    role_index = int(input("Select role: "))
    return principal_roles[role_index]


def assume_role(roleArn, principalArn, samlAssertion):
    conn = boto3.client('sts', config=client.Config(signature_version=botocore.UNSIGNED))
    aws_session_token = conn.assume_role_with_saml(
        RoleArn=roleArn,
        PrincipalArn=principalArn,
        SAMLAssertion=samlAssertion,
        DurationSeconds=3600,
    )
    
    return aws_session_token


