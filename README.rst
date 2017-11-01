awslogin
========

Python script for CLI and SDK access to AWS via ADFS while requiring MFA
access using `<https://duo.com/>`_

History and Purpose
-------------------

BYU used to use the great
`aws-adfs <https://github.com/venth/aws-adfs>`_ CLI tool to login to
our AWS accounts. It worked great, especially the DUO 2FA support.
Eventually, we decided to write our own similar tool but make it
BYU-specific so that we could tailor it to our needs (which basically
means hard-code certain BYU-specific things) and remove some of the
required parameters. Since this tool will be used by BYU employees only
we had that option. We then morphed it a little more for our use cases.
This isn't something that you could use outside of BYU, sorry.

Installation
------------

-  Python 3.6 is recommended but it should work with Python 2.7. See the `installation
   options <https://github.com/byu-oit/awslogin/blob/master/INSTALLATION_OPTIONS.md>`_ page for step by step
   instructions for installing in various environments.
-  See `<https://www.python.org/downloads/>`_ for a windows installation
   method.
-  In linux you may be able to use apt, rpm or
   `<https://www.python.org/downloads/>`_.
-  In Mac you can use homebrew, macports or
   `<https://www.python.org/downloads/>`_.
-  Run ``pip3 install byu_awslogin`` or ``pip install byu_awslogin`` as appropriate for your python installation

Upgrading
---------
If you already have byu_awslogin install and are looking to upgrade simply run

``pip3 install --upgrade byu_awslogin`` or ``pip install --upgrade byu_awslogin`` as appropriate for your python installation

Usage
-----

awslogin defaults to the default profile in your ~/.aws/config and
~/.aws/credentials files. ***If you already have a default profile you
want to save in your ~/.aws files make sure to do that before running
awslogin.***

Once you're logged in, you can execute commands using the AWS CLI or 
AWS SDK. Try running ``aws s3 ls``.

Currently, AWS temporary credentials are only valid for 1 hour. We cache your
ADFS session, however, so you can just re-run ``awslogin`` again to get a
new set of AWS credentials without logging in again to ADFS. Your ADFS login 
session is valid for 8 hours, after which time you'll be required to login 
to ADFS again to obtain a new session.

To switch accounts after you've already authenticated to an account, just
run awslogin again and select a new account/role combination.

To use it:

-  Run ``awslogin`` and it will prompt you for the AWS account and role
   to use.
-  Run ``awslogin --account <account name> --role <role name>`` to skip
   the prompting for account and name. You could specify just one of the
   arguments as well.
-  Run ``awslogin --profile <profile name>`` to specifiy an alternative
   profile
-  Run ``awslogin --region <region name>`` to specify a different region. The default region is *us-west-2*.
-  Run ``awslogin --status`` for the current status of the default profile
-  Run ``awslogin --status --profile dev`` for the current status of the
   dev profile
-  Run ``awslogin --status --profile all`` for the current status of the
   all profiles
-  Run ``awslogin --logout`` to logout of a cached ADFS session
-  Run ``awslogin --version`` to display the running version of awslogin
-  Run ``awslogin --help`` for full help message


Reporting bugs or requesting features
-------------------------------------

-  Enter an issue on the github repo.
-  Or, even better if you can, fix the issue and make a pull request.

Deploying changes
-----------------

-  Update the version.
-  Commit the change and push. Handel-codepipeline will run the
   automated tests and if they pass it will build and upload a new
   version to pypi.

TODO
----

-  Write tests
    - Write more tests to increase overall coverage
