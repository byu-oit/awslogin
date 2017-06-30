# awslogin
Python script for CLI and SDK access to AWS via ADFS while requiring MFA access using https://duo.com/

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
* Make sure you have python 3 installed.
* awslogin only works with python 3.
* Enter your [virtualenv](https://virtualenv.pypa.io/en/stable/) using python 3.
* Install twine by running `pip install twine`
* Make sure you have a '~/.pypirc' as defined [here](https://docs.python.org/3.2/distutils/packageindex.html#pypirc). See Paul for the login credentials.
* Run `python deploy.py`


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
