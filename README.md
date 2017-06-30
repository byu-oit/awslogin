# awslogin
Python script for CLI and SDK access to AWS via ADFS while requiring MFA access using https://duo.com/

## History and Purpose
BYU used to use the great [aws-adfs](https://github.com/venth/aws-adfs) CLI tool to login to our AWS accounts.  It worked great, especially the DUO 2FA support.  Eventually, we decided to write our own similar tool but make it BYU-specific so that we could taylor it to our needs (which basically means hard-code certain BYU-specific things) and remove some of the required parameters.  Since this tool will be used by BYU employees only we had that option.  We then morphed it a little more for our use cases.  This isn't something that you could use outside of BYU, sorry.

## Installation 
* Install Python 3.x using your preferred method.  
  * See https://www.python.org/downloads/ for a windows installation method.  
  * In linux you may be able to use apt, rpm or https://www.python.org/downloads/.
  * In Mac you can use homebrew, macports or https://www.python.org/downloads/.
* Run `pip3 install byu-awslogin`

## Usage
* Run `awslogin` and it will prompt you for the AWS account and role to use.
* Run `awslogin --account <account name> --role <role name>` to skip the prompting for account and name.  You could specify just one of the arcuments as well.

## Deploying changes
* Update the version in the VERSION file.
* Commit the change and push.  Handel-codepipeline will test and if the tests pass upload a new version to pypi.

## TODO
* gracefully handle the error case when the duo push is rejected
* Add support for profiles
* Authenticate once for 8 hours and rerun `awslogin` to relogin
* Simplify the adfs authentication code
* cache netid after subsequent logins ie default to last used
* Write tests
  * (David) adfs_auth.py 
  * (Nate) index.py
  * roles.py
  * assume_role.py
* Make a handel-codepipeline CI/CD pipeline with automated tests.  If they pass automatically deploy to pypi.
* [BUG] README.md and LICENSE get left over in /usr/local when pip install to mac
